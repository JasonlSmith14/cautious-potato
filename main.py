import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy import inspect

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

postgres_service = PostgresService(
    url=None,
    username=USERNAME,
    password=PASSWORD,
    port=PORT,
    database_name=DATABASE_NAME,
)

engine = postgres_service.engine

inspector = inspect(engine)
all_tables = inspector.get_table_names()

allowed_tables = [t for t in all_tables if t.startswith("gold_")]

db = SQLDatabase.from_uri(
    postgres_service.url,
    include_tables=allowed_tables,
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

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

questions_agent = Agent(
    "questions_agent",
    model_name="gemini-2.5-flash",
    model_provider="google_genai",
    prompt="Get the information related to the question",
    tools=toolkit.get_tools(),
)

embedding_model = Embeddings()

service = Service(
    database_service=postgres_service,
    extract=extract,
    parsing_agent=parsing_agent,
    categorising_agent=categorising_agent,
    embedding_model=embedding_model,
)


def main(service: Service):

    banking_statements = st.file_uploader(
        label="Upload your banking statements", accept_multiple_files=True, type="pdf"
    )

    if banking_statements:
        for banking_statement in banking_statements:
            file_path = f"data/{banking_statement.name}"
            with open(file_path, "wb") as file:
                file.write(banking_statement.getvalue())

            service.ingest_transactions(file_path=file_path)
            service.categorise_transactions()


if __name__ == "__main__":
    main(service=service)
