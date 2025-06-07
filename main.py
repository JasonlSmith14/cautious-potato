import os
import warnings
from dotenv import load_dotenv

from service import Service
from models.models import Transaction, Statement, StatementEmbeddings
from extract.extract import Extract
from extract.tika_parser import TikaParser
from extract.pytesseract_ocr import PytesseractOCR
from gemini import Gemini
from embeddings import Embeddings

warnings.filterwarnings(
    "ignore",
    message=r"PydanticSerializationUnexpectedValue\(Expected `list\[float\]`.*",
    category=UserWarning,
)


load_dotenv()

USERNAME = os.getenv("DATABASE_USERNAME")
PASSWORD = os.getenv("DATABASE_PASSWORD")
PORT = os.getenv("PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")
API_KEY = os.getenv("GEMINI_KEY")


def main():
    # Create tables
    service = Service(
        username=USERNAME,
        password=PASSWORD,
        port=PORT,
        database_name=DATABASE_NAME,
    )

    embeddings = Embeddings()

    service.delete_tables()
    service.create_tables()

    # Extract data from banking statement
    extract = Extract(parser=TikaParser(), ocr=PytesseractOCR())
    statement_embeddings = extract.extract(file_paths=["data/test.pdf"])

    statement_embeddings.parser_embedding = embeddings.create_embedding(
        statement_embeddings.parser_text[0]
    )
    statement_embeddings.ocr_embedding = embeddings.create_embedding(
        statement_embeddings.ocr_text[0][0]
    )

    statement_embeddings.embedding_model = embeddings.model_name

    # Parse data using model
    gemini = Gemini(api_key=API_KEY)
    transactions = gemini.generate_response(
        contents=(
            "Please parse the data below into valid JSON to create a list of Transaction objects. "
            "Provided is data from using both a parser and OCR. The data is based on the same document, use both to ensure all data is completely captured. "
            f"Here are details of the Transaction object: {Transaction.model_json_schema()}. Maku sure to only populate the required fields. "
            f"Parsed Data: {statement_embeddings.parser_text}"
            ""
            f"OCR Data: {statement_embeddings.ocr_text}"
        )
    )
    transactions = gemini.clean_and_parse_model_output(transactions)
    transactions = [Transaction(**t) for t in transactions]
    for transaction in transactions:
        description_embedding = embeddings.create_embedding(transaction.description)
        transaction.description_embedding = description_embedding

    dates = [transaction.date for transaction in transactions]

    statement = Statement(
        transactions=transactions,
        start_date=min(dates),
        end_date=max(dates),
        statement_embeddings=statement_embeddings,
    )

    service.create_single(model=statement)

    nandos_transaction = service.search_by_embedding(
        model=Transaction,
        embedding_column=Transaction.description_embedding,
        embedding=embeddings.create_embedding("Nandos"),
        limit=1,
    )

    print(nandos_transaction)


if __name__ == "__main__":
    main()
