import json
import time
from typing import List
from agent.agent import Agent
from database_service.base_database_service import BaseDatabaseService
from embeddings.base_embeddings import BaseEmbeddings
from extract.extract import Extract
from models.information import CategoryInformation, Transactions
from models.tables import Category, ParsedStatement, Statement, Transaction


class Service:

    def __init__(
        self,
        database_service: BaseDatabaseService,
        extract: Extract,
        parsing_agent: Agent,
        categorising_agent: Agent,
        embedding_model: BaseEmbeddings,
    ):
        self.database_service = database_service
        self.extract = extract
        self.parsing_agent = parsing_agent
        self.categorising_agent = categorising_agent
        self.embedding_model = embedding_model

        self.database_service.create_tables(
            tables=[
                Transaction.__table__,
                Category.__table__,
                Statement.__table__,
                ParsedStatement.__table__,
            ]
        )

    def ingest_transactions(self, file_path: str):
        parsed_statements = self.extract.extract_from_file(file_path=file_path)

        transactions: List[Transaction] = []
        for parsed_statement in parsed_statements:

            previously_parsed = self.database_service.read_with_filters(
                model=ParsedStatement,
                filters={
                    ParsedStatement.strategy_name: parsed_statement.strategy_name,
                    ParsedStatement.strategy_result: parsed_statement.strategy_result,
                },
            )

            if previously_parsed:
                continue

            transaction_information: Transactions = self.parsing_agent.invoke_agent(
                content=parsed_statement.strategy_result
            )

            transactions = transactions + [
                Transaction.model_validate(t)
                for t in transaction_information.transactions
            ]

        for transaction in transactions:
            transaction.description_embedding = self.embedding_model.create_embedding(
                text=transaction.description
            )

        if not transactions:
            return

        dates = [transaction.transaction_date for transaction in transactions]

        statement = Statement(
            transactions=transactions,
            start_date=min(dates),
            end_date=max(dates),
            parsed_statements=parsed_statements,
        )

        self.database_service.create_single(model=statement)

    def categorise_transactions(self):
        transaction_groups: List[List[Transaction]] = []
        uncategorised_transactions: List[Transaction] = (
            self.database_service.read_nulls(
                model=Transaction, column=Transaction.category_id
            )
        )
        for transaction in uncategorised_transactions:
            similar_transactions: List[Transaction] = (
                self.database_service.search_by_embedding(
                    embedding=transaction.description_embedding,
                    embedding_column=Transaction.description_embedding,
                    model=Transaction,
                    exclude_id=transaction.id,
                )
            )

            similar_uncategorised_transactions = [
                t for t in similar_transactions if t.category_id == None
            ]

            transaction_groups.append(similar_uncategorised_transactions)

        for transaction_group in transaction_groups:
            first_transaction = transaction_group[0]
            similar_transactions: List[Transaction] = (
                self.database_service.search_by_embedding(
                    embedding=first_transaction.description_embedding,
                    embedding_column=Transaction.description_embedding,
                    model=Transaction,
                    exclude_id=first_transaction.id,
                )
            )

            similar_transactions_with_categories = [
                t for t in similar_transactions if t.category_id != None
            ]

            if similar_transactions_with_categories:
                category = similar_transactions_with_categories[0].category

            else:
                average_amount = sum([t.amount for t in transaction_group]) / len(
                    transaction_group
                )
                descriptions = [t.description for t in transaction_group]
                category_information: CategoryInformation = (
                    self.categorising_agent.invoke_agent(
                        content=json.dumps(
                            {
                                "average_amount": average_amount,
                                "descriptions": descriptions,
                            }
                        )
                    )
                )

                category = Category.model_validate(category_information)

            category.transactions = transaction_group
            self.database_service.create_single(model=category)

        uncategorised_transactions: List[Transaction] = (
            self.database_service.read_nulls(
                model=Transaction, column=Transaction.category_id
            )
        )
        for transaction in uncategorised_transactions:

            category: CategoryInformation = self.categorising_agent.invoke_agent(
                content=transaction.model_dump_json(include={"description", "amount"})
            )

            category = Category.model_validate(category)

            category.transactions = [transaction]

            self.database_service.create_single(model=category)

            time.sleep(5)
