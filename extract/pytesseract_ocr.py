from typing import List
from PIL import Image
from pdf2image import convert_from_path
import pytesseract

from extract.base_ocr import BaseOCR


class PytesseractOCR(BaseOCR):
    def __init__(self):
        pass

    def _convert_from_path(self, pdf_path: str):
        return convert_from_path(pdf_path=pdf_path)

    def _image_to_string(self, page: Image):
        return pytesseract.image_to_string(page)

    def _scan_document(self, file_path: str):
        if file_path.endswith(".pdf"):
            pages = self._convert_from_path(pdf_path=file_path)
        elif file_path.endswith((".jpeg", ".png")):
            pages = [Image.open(fp=file_path)]

        return pages

    def scan_documents(self, file_paths: List[str]) -> List[List[str]]:
        documents_text = []
        for file_path in file_paths:
            pages = self._scan_document(file_path=file_path)
            page_texts = [self._image_to_string(page) for page in pages]
            documents_text.append(page_texts)
        return documents_text
