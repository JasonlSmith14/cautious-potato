from typing import List

from extract.base_ocr import BaseOCR
from extract.base_parser import BaseParser
from models.models import StatementEmbeddings


class Extract:
    def __init__(self, parser: BaseParser, ocr: BaseOCR):
        self.parser = parser
        self.ocr = ocr

    def extract(self, file_paths: List[str]):
        # TODO: Find a way to determine which strategy to use
        # Every page might be an image
        # Identify if images have useful information; logos for example are not important
        # Data may not be coherent; need a sanity check on extracted data based on quality
        parser_result = self.parser.parse_files(file_paths=file_paths)
        ocr_result = self.ocr.scan_documents(file_paths=file_paths)

        return StatementEmbeddings(parser_text=parser_result, ocr_text=ocr_result)
