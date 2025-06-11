from datetime import date
from typing import Any, List, Optional
from sqlmodel import Column, Relationship, SQLModel, Field
from pgvector.sqlalchemy import Vector

from enums.category import CategoryEnum
from enums.confidence_level import ConfidenceLevelEnum


class StatementEmbeddings(SQLModel, table=True):
    __tablename__ = "statement_embeddings"
    id: Optional[int] = Field(default=None, primary_key=True)
    statement_id: Optional[int] = Field(default=None, foreign_key="statements.id")

    parser_text: Optional[str] = Field(nullable=True)
    parser_embedding: Optional[Any] = Field(
        default=None, sa_column=Column(Vector(None))
    )

    ocr_text: Optional[str] = Field(nullable=True)
    ocr_embedding: Optional[Any] = Field(default=None, sa_column=Column(Vector(None)))

    statement: Optional["Statement"] = Relationship(
        back_populates="statement_embeddings"
    )

    embedding_model: Optional[str] = Field(default=None)


class Statement(SQLModel, table=True):
    __tablename__ = "statements"
    id: Optional[int] = Field(default=None, primary_key=True)

    start_date: date
    end_date: date

    transactions: List["Transaction"] = Relationship(back_populates="statement")
    statement_embeddings: Optional["StatementEmbeddings"] = Relationship(
        back_populates="statement"
    )


class CategoryInformation(SQLModel):
    category: CategoryEnum
    confidence_level: ConfidenceLevelEnum = Field(
        description="Confidence level in the category assignment."
    )


class DescriptionInformation(SQLModel):
    cleaned_description: str = Field(
        description="A cleaned and normalised version of the original transaction description."
    )


class ParsedInformation(SQLModel):
    transaction_date: date = Field(
        description="The exact date on which the transaction occurred."
    )
    description: str = Field(
        description="The raw, original description of the transaction as extracted from the bank statement."
    )

    description_embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(Vector(None)),
        description=(
            "A vector embedding representation of the cleaned description, used for semantic similarity searches. "
            "This facilitates matching transactions with similar descriptions for categorisation purposes."
        ),
    )
    amount: float = Field(
        description="The monetary value of the transaction, in South African Rand (ZAR)."
    )
    balance: float = Field(
        description="The account balance immediately after this transaction was applied."
    )


class TransactionInformation(SQLModel):
    parsed_information: ParsedInformation
    category_information: CategoryInformation
    description_information: DescriptionInformation


class Transaction(
    ParsedInformation, CategoryInformation, DescriptionInformation, table=True
):
    __tablename__ = "transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    statement_id: Optional[int] = Field(default=None, foreign_key="statements.id")

    statement: Optional["Statement"] = Relationship(back_populates="transactions")


class ParsedInformationInputs(SQLModel):
    parsed_information_inputs: List[ParsedInformation]


class CategoryInformationInputs(SQLModel):
    category_information_inputs: List[CategoryInformation]


class DescriptionformationInputs(SQLModel):
    category_information_inputs: List[DescriptionInformation]


class TransactionInformationInputs(SQLModel):
    transaction_information_inputs: List[TransactionInformation]
