import os
from dotenv import load_dotenv

from embeddings.embeddings import Embeddings
from models.information import CategoryInformation, Transactions
from database_service.postgres_database_service import PostgresService
from extract.extract import Extract
from extract.tika import TikaParser
from agent.agent import Agent
from service.service import Service

load_dotenv()


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

parser = TikaParser()
extract = Extract(parser=parser)

parsing_agent = Agent(
    name="parsing_agent",
    model_name="gemini-2.5-flash",
    model_provider="google_genai",
    prompt=(
        """You are responsible for processing banking statements to identify and extract individual transactions.

    For each transaction you must:
    1. Determine the correct transaction date. If the year is missing, infer it logically from the context of the statement and include it.
    2. Capture the original transaction description exactly as it appears in the statement.
    4. Identify the transaction amount and balance in South African Rand (ZAR).

    General guidelines:
    - Do not omit information if it is present in the statement.
    - When inferring missing data (e.g., the year), base it on strong contextual clues rather than guesswork.
    - Maintain accuracy and consistency across all transactions in the same statement."""
    ),
    tools=[],
    response_format=Transactions,
)

categorising_agent = Agent(
    name="categorising_agent",
    model_name="gemini-2.0-flash",
    model_provider="google_genai",
    prompt=(
        """You are responsible for categorising banking transactions.

    For a transaction you must:
    1. Determine the correct category given all the information about the transaction.
    2. Provide a reasoning for that category.
    3. Provide a cleaned description of the original description."""
    ),
    tools=[],
    response_format=CategoryInformation,
)

embedding_model = Embeddings()

service = Service(
    database_service=postgres_service,
    extract=extract,
    parsing_agent=parsing_agent,
    categorising_agent=categorising_agent,
    embedding_model=embedding_model,
)


def main(file_path: str, service: Service):
    service.ingest_transactions(file_path=file_path)
    service.categorise_transactions()


if __name__ == "__main__":
    main(file_path="data/13-08-25.pdf", service=service)
