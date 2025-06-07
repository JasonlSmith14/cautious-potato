from abc import ABC, abstractmethod
from typing import List


class BaseParser(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def parse_files(self, file_paths: List[str]):
        pass
