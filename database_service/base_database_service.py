from abc import ABC, abstractmethod
from typing import List

from sqlmodel import SQLModel


class BaseDatabaseService(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def create_single(self, model: SQLModel):
        pass

    @abstractmethod
    def create_tables(self, tables: List[str]):
        pass
