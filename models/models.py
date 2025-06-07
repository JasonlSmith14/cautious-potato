from datetime import date
from enum import Enum
from typing import Any, List, Optional
from sqlmodel import Column, Relationship, SQLModel, Field
from pgvector.sqlalchemy import Vector


class CategoryEnum(str, Enum):
    food = "food"
    groceries = "groceries"
    rent = "rent"
    utilities = "utilities"
    transport = "transport"
    entertainment = "entertainment"
    health = "health"
    education = "education"
    shopping = "shopping"
    subscriptions = "subscriptions"
    travel = "travel"
    income = "income"
    investment = "investment"
    insurance = "insurance"
    fees = "fees"
    charity = "charity"
    miscellaneous = "miscellaneous"
    unknown = "unknown"


class StatementEmbeddings(SQLModel, table=True):
    __tablename__ = "statement_embeddings"
    id: Optional[int] = Field(default=None, primary_key=True)
    statement_id: Optional[int] = Field(default=None, foreign_key="statements.id")

    parser_embedding: Optional[Any] = Field(
        default=None, sa_column=Column(Vector(None))
    )
    parser_text: str

    ocr_text: str
    ocr_embedding: Optional[Any] = Field(default=None, sa_column=Column(Vector(None)))

    statement: Optional["Statement"] = Relationship(
        back_populates="statement_embeddings"
    )

    embedding_model: Optional[str] = Field(default=None)


class Statement(SQLModel, table=True):
    __tablename__ = "statements"
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(back_populates="statement")
    start_date: date
    end_date: date

    statement_embeddings: Optional["StatementEmbeddings"] = Relationship(
        back_populates="statement"
    )


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    statement_id: Optional[int] = Field(default=None, foreign_key="statements.id")
    date: date
    description: str
    description_embedding: Optional[Any] = Field(
        default=None, sa_column=Column(Vector(None))
    )
    category: CategoryEnum
    amount: float
    balance: float

    statement: Optional["Statement"] = Relationship(back_populates="transactions")
