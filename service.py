from typing import List, Optional, Type

import pandas as pd
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.orm.attributes import InstrumentedAttribute


class Service:
    def __init__(
        self,
        username: Optional[str],
        password: Optional[str],
        port: Optional[str],
        database_name: Optional[str],
    ):
        self.username = username
        self.password = password
        self.port = port
        self.database_name = database_name

        self.engine = create_engine(self._build_postgresql_url())

    def _build_postgresql_url(self):
        return f"postgresql://{self.username}:{self.password}@localhost:{self.port}/{self.database_name}"

    def create_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def delete_tables(self):
        SQLModel.metadata.drop_all(self.engine)

    def create_single(self, model: Type[SQLModel]):
        with Session(self.engine) as session:
            session.add(model)
            session.commit()

    def read_all(self, model: Type[SQLModel]):
        with Session(self.engine) as session:
            statement = select(model)
            items = session.exec(statement).all()
            return items

    def all_to_csv(self, model: Type[SQLModel], file_name: str):
        items = self.read_all(model=model)
        data = pd.DataFrame([item.model_dump() for item in items])
        data.to_csv(f"{file_name}.csv", index=False)

    def create_many(self, models: List[SQLModel]):
        for model in models:
            self.create_single(model=model)

    def delete_all(self, model: Type[SQLModel]):
        with Session(self.engine) as session:
            statement = select(model)
            items = session.exec(statement).all()

            for item in items:
                session.delete(item)
                session.commit()

    def search_by_embedding(
        self,
        embedding: List[float],
        embedding_column: InstrumentedAttribute,
        model: Type[SQLModel],
        limit: int = 10,
    ):
        with Session(self.engine) as session:
            statement = (
                select(model)
                .order_by(embedding_column.op("<=>")(embedding))
                .limit(limit)
            )
            results = session.exec(statement).all()
            return results
