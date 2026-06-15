from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class Category(BaseModel):
    id: int
    title: str
    description: str
    monthly_limit: float


class Tag(BaseModel):
    id: int
    name: str
    description: str


class Transaction(BaseModel):
    id: int
    transaction_type: TransactionType
    title: str
    amount: float
    category: Category
    tags: Optional[List[Tag]] = Field(default_factory=list)


class TransactionResponse(TypedDict):
    status: int
    data: Transaction


class CategoryResponse(TypedDict):
    status: int
    data: Category


class TagResponse(TypedDict):
    status: int
    data: Tag
