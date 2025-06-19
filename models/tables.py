from datetime import date
from typing import Any, List, Optional
from sqlmodel import Column, Relationship, SQLModel, Field
from pgvector.sqlalchemy import Vector

from models.information import TransactionInformation


class ParsedStatement(SQLModel, table=True):
    __tablename__ = "parsed_statements"
    id: Optional[int] = Field(default=None, primary_key=True)
    statement_id: Optional[int] = Field(default=None, foreign_key="statements.id")
    strategy_name: str
    strategy_result: str

    statement: Optional["Statement"] = Relationship(back_populates="parsed_statements")


class Statement(SQLModel, table=True):
    __tablename__ = "statements"
    id: Optional[int] = Field(default=None, primary_key=True)

    start_date: date
    end_date: date

    transactions: List["Transaction"] = Relationship(back_populates="statement")
    parsed_statements: List["ParsedStatement"] = Relationship(
        back_populates="statement"
    )


class Transaction(TransactionInformation, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    statement_id: Optional[int] = Field(default=None, foreign_key="statements.id")
    statement: Optional["Statement"] = Relationship(back_populates="transactions")
