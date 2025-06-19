import os
from typing import List
from dotenv import load_dotenv

from models.inputs import CategoryInformationInputs, ParsedInformationInputs
from models.tables import Statement, ParsedStatement, Transaction
from service import Service

from extract.extract import Extract
from extract.tika_parser import TikaParser
from embeddings.embeddings import Embeddings
from agent.agent import Agent
from agent.agent_chain import AgentChain

load_dotenv()

USERNAME = os.getenv("DATABASE_USERNAME")
PASSWORD = os.getenv("DATABASE_PASSWORD")
PORT = os.getenv("PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")
API_KEY = os.getenv("GEMINI_KEY")


service = Service(
    url=None,
    username=USERNAME,
    password=PASSWORD,
    port=PORT,
    database_name=DATABASE_NAME,
)
embeddings = Embeddings()

extract = Extract(parsers=[TikaParser()])


parsing_agent = Agent[ParsedInformationInputs](
    name="parsing_agent",
    model_name="gemini-2.0-flash",
    model_provider="google_genai",
    prompt=(
        "You are responsible for extracting transactions from a banking statement. "
        "Each transaction may include a date, original description, amount, and balance. "
        "You will be provided with both structured and OCR-based extractions of the same statement."
    ),
    tools=[],
    response_format=ParsedInformationInputs,
)


categorising_agent = Agent[CategoryInformationInputs](
    name="categorising_agent",
    model_name="gemini-2.0-flash",
    model_provider="google_genai",
    prompt=(
        "You are responsible for categorising banking transactions using their description and amount. "
        "Additionally, return a cleaned and readable version of the original transaction description. "
        "Tool-usage is highly encouraged. "
        "Ensure your queries are well-formed and include relevant context, such as the transaction location, to improve search accuracy."
    ),
    tools=[],
    response_format=CategoryInformationInputs,
)

agent_chain = AgentChain(
    parsing_agent=parsing_agent,
    categorising_agent=categorising_agent,
)


def main():
    # service.delete_tables()
    service.create_tables(
        tables=[
            Statement.__table__,
            Transaction.__table__,
            ParsedStatement.__table__,
        ]
    )

    # This is to extract the data from the banking statement
    parsed_statements = extract.extract_from_file(file_path="data/test.pdf")

    transaction_information = agent_chain.process_transactions(
        parsed_statements=parsed_statements
    )

    transactions: List[Transaction] = [
        Transaction.model_validate(t) for t in transaction_information
    ]

    # Create the embeddings of the transaction descriptions
    for transaction in transactions:
        transaction.description_embedding = embeddings.create_embedding(
            transaction.description
        )

    # Get a list of the dates of the transactions
    dates = [transaction.transaction_date for transaction in transactions]

    # Build the statement
    statement = Statement(
        transactions=transactions,
        start_date=min(dates),
        end_date=max(dates),
        parsed_statements=parsed_statements,
    )

    # Add to table
    service.create_single(model=statement)


if __name__ == "__main__":
    main()
