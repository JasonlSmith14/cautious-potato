import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import logging

from database_service.base_database_service import BaseDatabaseService
from embeddings.base_embeddings import BaseEmbeddings
from embeddings.embeddings import Embeddings
from embeddings.gemini_embeddings import LangchainEmbeddings
from models.information import Transactions
from models.tables import ParsedStatement, Statement, Transaction
from database_service.postgres_database_service import PostgresService

from extract.extract import Extract
from extract.tika import TikaParser
from agent.agent import Agent

load_dotenv()

logging.basicConfig(level=logging.INFO)

USERNAME = os.getenv("DATABASE_USERNAME")
PASSWORD = os.getenv("DATABASE_PASSWORD")
PORT = os.getenv("PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

API_KEY = os.getenv("GEMINI_KEY")


postgres_service = PostgresService(
    url=None,
    username=USERNAME,
    password=PASSWORD,
    port=PORT,
    database_name=DATABASE_NAME,
)

# gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
# langchain_embeddings = LangchainEmbeddings(embedding_model=gemini_embeddings)

embeddings = Embeddings()

parser = TikaParser()

extract = Extract(parser=parser)


transaction_agent = Agent(
    name="transaction_agent",
    model_name="gemini-2.5-flash",
    model_provider="google_genai",
    prompt=(
        """You are responsible for processing banking statements to identify and extract individual transactions.

    For each transaction you must:
    1. Determine the correct transaction date. If the year is missing, infer it logically from the context of the statement and include it.
    2. Capture the original transaction description exactly as it appears in the statement.
    3. Create a cleaned, readable version of the description by removing irrelevant text, numbers, or codes, keeping only the merchant or meaningful entity name.
    4. Identify the transaction amount and balance in South African Rand (ZAR).
    5. Assign a thoughtful, context-appropriate category based on the transaction's description and amount.
    6. Provide a clear and reasonable justification for the chosen category.

    General guidelines:
    - Avoid vague category choices unless truly unavoidable.
    - Do not omit information if it is present in the statement.
    - When inferring missing data (e.g., the year), base it on strong contextual clues rather than guesswork.
    - Maintain accuracy and consistency across all transactions in the same statement."""
    ),
    tools=[],
    response_format=Transactions,
)


def main(
    file_path: str,
    database_service: BaseDatabaseService,
    transaction_agent: Agent,
    embeddings_model: BaseEmbeddings,
    extract: Extract,
):
    database_service.create_tables(
        tables=[
            Statement.__table__,
            Transaction.__table__,
            ParsedStatement.__table__,
        ]
    )

    parsed_statements = extract.extract_from_file(file_path=file_path)

    logging.info(f"There are {len(parsed_statements)} pages to process")

    transactions: List[Transaction] = []
    for parsed_statement in parsed_statements:
        logging.info(f"Processing page {parsed_statements.index(parsed_statement) + 1}")
        transaction_information: Transactions = transaction_agent.invoke_agent(
            content=parsed_statement.strategy_result
        )

        transactions = transactions + [
            Transaction.model_validate(t) for t in transaction_information.transactions
        ]
        logging.info(f"Processed {len(transactions)} transactions")

    for transaction in transactions:
        transaction.description_embedding = embeddings_model.create_embedding(
            transaction.description
        )

    dates = [transaction.transaction_date for transaction in transactions]

    statement = Statement(
        transactions=transactions,
        start_date=min(dates),
        end_date=max(dates),
        parsed_statement=[parsed_statement],
    )

    database_service.create_single(model=statement)


if __name__ == "__main__":
    main(
        file_path="data/13-08-25.pdf",
        database_service=postgres_service,
        transaction_agent=transaction_agent,
        embeddings_model=embeddings,
        extract=extract,
    )
