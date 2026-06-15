from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class TransactionTagLink(SQLModel, table=True):
    __tablename__ = "transaction_tag_link"

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


class User(SQLModel, table=True):
    __tablename__ = "app_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, sa_column_kwargs={"unique": True})
    email: str = Field(index=True, sa_column_kwargs={"unique": True})
    hashed_password: str
    is_active: bool = True

    categories: List["Category"] = Relationship(back_populates="user")
    tags: List["Tag"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    monthly_limit: float
    user_id: int = Field(foreign_key="app_user.id")

    user: Optional[User] = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    user_id: int = Field(foreign_key="app_user.id")

    user: Optional[User] = Relationship(back_populates="tags")
    transactions: List["Transaction"] = Relationship(
        back_populates="tags",
        link_model=TransactionTagLink,
    )


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_type: TransactionType
    title: str
    amount: float
    operation_date: date
    description: Optional[str] = None
    user_id: int = Field(foreign_key="app_user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    user: Optional[User] = Relationship(back_populates="transactions")
    category: Optional[Category] = Relationship(back_populates="transactions")
    tags: List[Tag] = Relationship(
        back_populates="transactions",
        link_model=TransactionTagLink,
    )


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    amount: float
    period_start: date
    period_end: date
    user_id: int = Field(foreign_key="app_user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    user: Optional[User] = Relationship(back_populates="budgets")
    category: Optional[Category] = Relationship(back_populates="budgets")


class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    target_amount: float
    current_amount: float = 0
    deadline: Optional[date] = None
    is_completed: bool = False
    user_id: int = Field(foreign_key="app_user.id")

    user: Optional[User] = Relationship(back_populates="goals")


class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    message: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="app_user.id")

    user: Optional[User] = Relationship(back_populates="notifications")
