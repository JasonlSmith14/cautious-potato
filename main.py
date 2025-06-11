import os
from typing import List
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from service import Service
from models.models import (
    CategoryInformationInputs,
    DescriptionformationInputs,
    ParsedInformationInputs,
    Transaction,
    Statement,
    TransactionInformationInputs,
)
from extract.extract import Extract
from extract.parser.tika_parser import TikaParser
from extract.ocr.pytesseract_ocr import PytesseractOCR
from embeddings.embeddings import Embeddings
from tools.tools import Tools
from agent.agent import Agent

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

extract = Extract(
    parser=TikaParser(),
    ocr=PytesseractOCR(),
    embeddings=embeddings,
    use_parser=True,
    use_ocr=False,
)

duck_duck_go_tool = Tools.duck_duck_go_tool()


@tool(
    description="Use this tool to search for similar transactions using the description embedding. This is to help with categorising transactions"
)
def search_by_embedding_tool(embedding: List[float]) -> Transaction:
    return service.search_by_embedding(
        embedding=embedding,
        embedding_column=Transaction.description_embedding,
        model=Transaction,
        limit=5,
    )


parsing_agent = Agent[ParsedInformationInputs](
    name="parsing_agent",
    model_name="gemini-2.0-flash",
    model_provider="google_genai",
    prompt=(
        "You are responsible for extracting transactions from a banking statement. "
        "Each transaction may include a date, original description, amount, and balance. "
        "You will be provided with both structured and OCR-based extractions of the same statement.\n\n"
        "Instructions:\n"
        "1. Cross-reference both sources to extract accurate transactions.\n"
        "2. If a field is missing in one source but present in another, prefer the one with more complete or reliable information.\n"
        "3. Only populate fields that can be directly inferred from the source data.\n"
        "4. Do not generate data or guess missing information.\n\n"
        "Return a list of transactions with only raw extracted values."
    ),
    tools=[],
    response_format=ParsedInformationInputs,
).create_agent()


categorising_agent = Agent[CategoryInformationInputs](
    name="categorising_agent",
    model_name="gemini-2.0-flash",
    model_provider="google_genai",
    prompt=(
        "You are responsible for categorising banking transactions using their description and amount. "
        "You must also return a cleaned, readable version of the original transaction description.\n\n"
        "Instructions:\n"
        "1. For each transaction, examine the description and amount.\n"
        "2. Clean the description by removing non-informative characters, normalising whitespace, and standardising case.\n"
        "3. Use the cleaned description and amount to determine the most appropriate category from the available options.\n"
        "4. Consider semantic meaning, abbreviations, merchant names, and spending patterns.\n"
        "5. Only assign a category if you are confident. If uncertain, assign the closest reasonable category.\n\n"
        "Do not make up data. Only use the provided description and amount for decision-making."
    ),
    tools=[],
    response_format=CategoryInformationInputs,
).create_agent()

description_agent = Agent[DescriptionformationInputs](
    name="description_agent",
    model_name="gemini-2.0-flash",
    model_provider="google_genai",
    prompt=(
        "You are responsible for cleaning transaction descriptions to make them clear, readable, and standardized.\n\n"
        "Instructions:\n"
        "1. Remove non-informative characters (e.g., excessive punctuation, long alphanumeric IDs, stray symbols).\n"
        "2. Normalize whitespace (e.g., remove extra spaces, tabs, and line breaks).\n"
        "3. Standardize case appropriately:\n"
        "   - Use Title Case for names and merchants (e.g., 'starbucks coffee' → 'Starbucks Coffee').\n"
        "   - Uppercase acronyms (e.g., 'atm', 'eft' → 'ATM', 'EFT').\n"
        "4. Preserve meaningful information (e.g., merchant names, locations, dates if relevant).\n"
        "5. Do not change or add information that isn't clearly present in the original description.\n\n"
        "Your output must contain only the cleaned, readable transaction description."
    ),
    tools=[],
    response_format=DescriptionformationInputs,
).create_agent()

supervisor = create_supervisor(
    model=init_chat_model("gemini-2.0-flash", model_provider="google_genai"),
    agents=[parsing_agent, categorising_agent, description_agent],
    prompt=(
        "You are the supervisor and compiler in a multi-agent system that processes banking statements.\n\n"
        "Your responsibilities:\n"
        "1. Provide structured and OCR-based extracts to the parsing agent.\n"
        "2. Receive a list of parsed transactions from the parsing agent.\n"
        "3. For each parsed transaction, forward *only* the `description` and `amount` to the categorising agent.\n"
        "4. Receive categorised output.\n"
        "5. Merge the parsing outputs with the categorisation outputs.\n\n"
        "Guidelines:\n"
        "- Do not perform parsing or categorisation yourself.\n"
        "- Only use the values explicitly provided by the agents — do not fabricate or infer missing data.\n"
        "- If there's a conflict (e.g. mismatch in description), prefer the version that is cleaner or more complete.\n"
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
    response_format=TransactionInformationInputs,
).compile()


def main():
    service.delete_tables()
    service.create_tables()

    # This is to extract the data from the banking statement
    statement_embeddings = extract.extract_from_file(file_path="data/test.pdf")

    # Retrieve all transactions from the banking statement. Simply parsed data
    transaction_information_inputs = supervisor.invoke(
        input={
            "messages": [
                HumanMessage(
                    content=(
                        f"Parsed Data:\n\n{statement_embeddings.parser_text}\n\n"
                        f"OCR Data:\n\n{statement_embeddings.ocr_text}"
                    )
                )
            ]
        }
    )

    transaction_information_inputs: TransactionInformationInputs = (
        transaction_information_inputs["structured_response"]
    )
    transactions: List[Transaction] = [
        Transaction.model_validate(t)
        for t in transaction_information_inputs.transaction_information_inputs
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
        statement_embeddings=statement_embeddings,
    )

    # Add to table
    service.create_single(model=statement)


if __name__ == "__main__":
    main()
