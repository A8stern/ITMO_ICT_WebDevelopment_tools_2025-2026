from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel
from typing_extensions import TypedDict


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(
        default=None,
        foreign_key="transaction.id",
        primary_key=True,
    )
    tag_id: Optional[int] = Field(
        default=None,
        foreign_key="tag.id",
        primary_key=True,
    )
    importance_level: Optional[int] = None


class TransactionTagLinkDefault(SQLModel):
    transaction_id: int
    tag_id: int
    importance_level: Optional[int] = None


class CategoryDefault(SQLModel):
    title: str
    description: str
    monthly_limit: float


class Category(CategoryDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(back_populates="category")


class CategoryRead(CategoryDefault):
    id: int


class TagDefault(SQLModel):
    name: str
    description: str


class Tag(TagDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(
        back_populates="tags",
        link_model=TransactionTagLink,
    )


class TagRead(TagDefault):
    id: int


class TransactionDefault(SQLModel):
    transaction_type: TransactionType
    title: str
    amount: float
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Transaction(TransactionDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: Optional[Category] = Relationship(back_populates="transactions")
    tags: List[Tag] = Relationship(
        back_populates="transactions",
        link_model=TransactionTagLink,
    )


class TransactionRead(TransactionDefault):
    id: int
    category: Optional[CategoryRead] = None
    tags: List[TagRead] = Field(default_factory=list)


class TransactionTagLinkRead(TransactionTagLinkDefault):
    pass


class TransactionResponse(TypedDict):
    status: int
    data: Transaction


class CategoryResponse(TypedDict):
    status: int
    data: Category


class TagResponse(TypedDict):
    status: int
    data: Tag


class TransactionTagLinkResponse(TypedDict):
    status: int
    data: TransactionTagLink
