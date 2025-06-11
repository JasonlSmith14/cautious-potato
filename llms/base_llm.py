from abc import ABC, abstractmethod


class BaseLLM(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def generate_response(self, input: str):
        pass
