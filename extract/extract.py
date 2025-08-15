from typing import List
from extract.parser import Parser
from models.tables import ParsedStatement
from pypdf import PdfReader, PdfWriter
import os


class Extract:
    def __init__(self, parser: Parser):
        self.parser = parser

    def _split_pdf_to_pages(self, file_path: str, output_folder: str):
        reader = PdfReader(file_path)

        output_files = []
        for i, page in enumerate(reader.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)

            output_path = f"{output_folder}/page_{i}.pdf"
            with open(output_path, "wb") as output_pdf:
                writer.write(output_pdf)

            output_files.append(output_path)

        return output_files

    def extract_from_file(self, file_path: str) -> List[ParsedStatement]:

        output_folder = file_path.split(".")[0]
        os.makedirs(output_folder, exist_ok=True)

        file_paths = self._split_pdf_to_pages(
            file_path=file_path, output_folder=output_folder
        )
        parsed_results = self.parser.parse_documents(file_paths=file_paths)

        parsed_statements = []
        for parsed_result in parsed_results:
            parsed_statement = ParsedStatement(
                strategy_name=self.parser.__class__.__name__,
                strategy_result=parsed_result,
            )
            parsed_statements.append(parsed_statement)

        return parsed_statements
