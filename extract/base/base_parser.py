from abc import ABC, abstractmethod
from typing import List


class BaseParser(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def parse_file(self, file_path: str) -> str:
        pass

    @abstractmethod
    def parse_files(self, file_paths: List[str]) -> List[str]:
        pass
