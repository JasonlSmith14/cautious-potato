from datetime import date
from typing import List, Optional
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from enums.category import CategoryEnum


class TransactionInformation(SQLModel, table=False):
    transaction_date: date = Field(
        description="The exact date of the transaction, in ISO format YYYY-MM-DD."
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
        description="The monetary value of the transaction, in South African Rand (ZAR). Should be positive for money coming into the account, and negative for money leaving the account."
    )
    balance: float = Field(
        description="The account balance immediately after this transaction was applied."
    )
    category: CategoryEnum = Field(
        description="The category the transaction belongs to. This should be thought-out well and not naively chosen."
    )
    reasoning: str = Field(
        description="The reason for choosing the category. Should be well-explained and reasonable."
    )
    cleaned_description: str = Field(
        description="A cleaned and normalised version of the transaction description. For example, 'DEBIT CARD PURCHASE FROM 65.00- 04 22 MILKY LANE MO 5196*7245 16 APR' should be 'Milky Lane'"
    )


class Transactions(SQLModel, table=False):
    transactions: List[TransactionInformation]
