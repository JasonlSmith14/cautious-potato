from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, TypeVar

from sqlmodel import SQLModel
from sqlalchemy.orm.attributes import InstrumentedAttribute

T = TypeVar("T", bound=SQLModel)


class BaseDatabaseService(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def create_single(self, model: Type[T]):
        pass

    @abstractmethod
    def update_single(self, model: Type[T], model_id: int, update_data: Type[T]):
        pass

    @abstractmethod
    def create_tables(self, tables: List[str]):
        pass

    @abstractmethod
    def read_nulls(
        self, model: Type[T], column: InstrumentedAttribute
    ) -> List[Type[T]]:
        pass

    @abstractmethod
    def read_with_filters(
        self, model: Type[T], filters: Dict[InstrumentedAttribute, Any]
    ) -> List[Type[T]]:
        pass

    @abstractmethod
    def search_by_embedding(
        self,
        embedding: List[float],
        embedding_column: InstrumentedAttribute,
        model: Type[T],
        limit: int,
        threshold: float,
        exclude_id: int,
    ) -> List[T]:
        pass
