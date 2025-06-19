from abc import ABC, abstractmethod
from typing import List


class Parser(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def parse_document(self, file_path: str) -> str:
        pass

    @abstractmethod
    def parse_documents(self, file_paths: List[str]) -> List[str]:
        pass
