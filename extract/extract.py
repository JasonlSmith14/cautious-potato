from typing import List, Optional

from embeddings.base_embeddings import BaseEmbeddings
from extract.base.base_ocr import BaseOCR
from extract.base.base_parser import BaseParser
from models.models import StatementEmbeddings


class Extract:
    def __init__(
        self,
        parser: BaseParser,
        ocr: BaseOCR,
        embeddings: BaseEmbeddings,
        use_parser: bool = True,
        use_ocr: bool = True,
    ):
        self.parser = parser
        self.ocr = ocr
        self.embeddings = embeddings
        self.use_parser = use_parser
        self.use_ocr = use_ocr

    def extract_from_file(self, file_path: str) -> StatementEmbeddings:
        parser_text = parser_embedding = None
        ocr_text = ocr_embedding = None

        if self.use_parser:
            parser_text = self.parser.parse_file(file_path)
            parser_embedding = self.embeddings.create_embedding(parser_text)

        if self.use_ocr:
            ocr_text = self.ocr.scan_document(file_path)
            ocr_embedding = self.embeddings.create_embedding(ocr_text)

        return StatementEmbeddings(
            parser_text=parser_text,
            ocr_text=ocr_text,
            parser_embedding=parser_embedding,
            ocr_embedding=ocr_embedding,
            embedding_model=self.embeddings.model_name,
        )
