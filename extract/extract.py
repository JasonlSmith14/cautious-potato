from typing import List
from extract.parser import Parser
from models.tables import ParsedStatement


class Extract:
    def __init__(
        self,
        parsers: List[Parser],
    ):
        self.parsers = parsers

    def extract_from_file(self, file_path: str) -> List[ParsedStatement]:
        parsed_statements = []
        for parser in self.parsers:
            parsed_result = parser.parse_document(file_path=file_path)
            parsed_statement = ParsedStatement(
                strategy_name=parser.__class__.__name__, strategy_result=parsed_result
            )
            parsed_statements.append(parsed_statement)

        return parsed_statements
