from typing import List
from extract.parser import Parser
from models.tables import ParsedStatement


class Extract:
    def __init__(self, parser: Parser):
        self.parser = parser

    def extract_from_file(self, file_path: str) -> ParsedStatement:

        parsed_result = self.parser.parse_document(file_path=file_path)
        parsed_statement = ParsedStatement(
            strategy_name=self.parser.__class__.__name__, strategy_result=parsed_result
        )

        return parsed_statement
