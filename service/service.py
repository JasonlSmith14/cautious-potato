import time
from typing import List
import uuid
from agent.agent import Agent
from database_service.base_database_service import BaseDatabaseService
from embeddings.base_embeddings import BaseEmbeddings
from enums.category import CategoryEnum
from extract.extract import Extract
from models.information import Categories, CategoryInformation, Transactions
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

    def extract_transactions(self, file_path: str):
        return self.extract.extract_from_file(file_path=file_path)

    def parse_transactions(self, parsed_statements: List[ParsedStatement]):

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

        return transactions

    def create_statement(
        self, transactions: List[Transaction], parsed_statements: List[ParsedStatement]
    ):

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

    def ingest_transactions(self, file_path: str):
        parsed_statements = self.extract_transactions(file_path=file_path)
        transactions = self.parse_transactions(parsed_statements=parsed_statements)
        self.create_statement(
            transactions=transactions, parsed_statements=parsed_statements
        )

    def categorise_transactions(self):
        """
        1. Go through each transaction to find similar categorised transactions to determine the category
        2. Then find all simililar uncategorised transactions, determine the category for one then pass that through to each transaction
        3. Finally, determine the categories for all the remaining transactions all at once, or in batches
        """

        # Step 1
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

            if similar_transactions:
                category_id = similar_transactions[0].category_id
                if category_id:

                    transaction.category_id = category_id
                    self.database_service.update_single(
                        model=Transaction,
                        model_id=transaction.id,
                        update_data=transaction.model_dump(include={"category_id"}),
                    )

                    continue

        # Step 2
        attempted_all_transactions = False
        while not attempted_all_transactions:
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
                        limit=10000,
                        model=Transaction,
                        exclude_id=transaction.id,
                    )
                )

                # Group all similar uncategorised transactions
                similar_transactions = [
                    similar_transaction
                    for similar_transaction in similar_transactions
                    if similar_transaction.category_id == None
                ]

                if similar_transactions:
                    # Determine the category for the first transaction
                    category: CategoryInformation = (
                        self.categorising_agent.invoke_agent(
                            content=similar_transactions[0].model_dump_json(
                                include={"description", "amount"}
                            )
                        )
                    )

                    category = Category.model_validate(category)
                    category.transactions = similar_transactions
                    self.database_service.create_single(model=category)

                    break

                attempted_all_transactions = True

        # Step 3
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

            time.sleep(30)
