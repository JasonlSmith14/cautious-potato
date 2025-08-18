from typing import List
from agent.agent import Agent
from database_service.base_database_service import BaseDatabaseService
from extract.extract import Extract
from models.information import Transactions
from models.tables import Category, ParsedStatement, Statement, Transaction


class Service:

    def __init__(
        self,
        database_service: BaseDatabaseService,
        extract: Extract,
        parsing_agent: Agent,
        categorising_agent: Agent,
    ):
        self.database_service = database_service
        self.extract = extract
        self.parsing_agent = parsing_agent
        self.categorising_agent = categorising_agent

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
            transaction_information: Transactions = self.parsing_agent.invoke_agent(
                content=parsed_statement.strategy_result
            )

            transactions = transactions + [
                Transaction.model_validate(t)
                for t in transaction_information.transactions
            ]

        return transactions

    def create_statement(
        self, transactions: List[Transaction], parsed_statements: List[ParsedStatement]
    ):
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
        pass
