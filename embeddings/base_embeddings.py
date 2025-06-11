from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddings(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def create_embedding(self, text: str) -> List[float]:
        pass
