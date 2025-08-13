import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from database_service.base_database_service import BaseDatabaseService
from embeddings.base_embeddings import BaseEmbeddings
from embeddings.gemini_embeddings import LangchainEmbeddings
from models.information import Transactions
from models.tables import ParsedStatement, Statement, Transaction
from database_service.postgres_database_service import PostgresService

from extract.extract import Extract
from extract.tika import TikaParser
from agent.agent import Agent

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

gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

langchain_embeddings = LangchainEmbeddings(embedding_model=gemini_embeddings)

parser = TikaParser()

extract = Extract(parser=parser)


transaction_agent = Agent(
    name="transaction_agent",
    model_name="gemini-2.0-flash",
    model_provider="google_genai",
    prompt=(
        "You are responsible for extracting transactions from a banking statement. "
        "You are also responsible for categorising banking transactions using their description and amount. "
        "Additionally, return a cleaned and readable version of the original transaction description. "
    ),
    tools=[],
    response_format=Transactions,
)


def main(
    database_service: BaseDatabaseService,
    transaction_agent: Agent,
    embeddings_model: BaseEmbeddings,
    extract: Extract,
):
    # database_service.delete_tables(
    #     tables=[
    #         Statement.__table__,
    #         Transaction.__table__,
    #         ParsedStatement.__table__,
    #     ]
    # )
    # database_service.create_tables(
    #     tables=[
    #         Statement.__table__,
    #         Transaction.__table__,
    #         ParsedStatement.__table__,
    #     ]
    # )

    # This is to extract the data from the banking statement
    parsed_statement = extract.extract_from_file(file_path="data/13-08-25.pdf")

    transaction_information: Transactions = transaction_agent.invoke_agent(
        content=parsed_statement.strategy_result
    )

    transactions: List[Transaction] = [
        Transaction.model_validate(t) for t in transaction_information.transactions
    ]

    # Create the embeddings of the transaction descriptions
    for transaction in transactions:
        transaction.description_embedding = embeddings_model.create_embedding(
            transaction.description
        )

    # Get a list of the dates of the transactions
    dates = [transaction.transaction_date for transaction in transactions]

    # Build the statement
    statement = Statement(
        transactions=transactions,
        start_date=min(dates),
        end_date=max(dates),
        parsed_statement=[parsed_statement],
    )

    # Add to table
    database_service.create_single(model=statement)


if __name__ == "__main__":
    main(
        database_service=postgres_service,
        transaction_agent=transaction_agent,
        embeddings_model=langchain_embeddings,
        extract=extract,
    )
