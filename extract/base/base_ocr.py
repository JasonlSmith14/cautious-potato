from abc import ABC, abstractmethod
from typing import List


class BaseOCR(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def scan_document(self, file_path: str) -> str:
        pass

    @abstractmethod
    def scan_documents(self, file_paths: List[str]) -> List[str]:
        pass
