from datetime import date, datetime
from typing import List, Optional

from sqlmodel import Field, SQLModel
from typing_extensions import TypedDict

from app.models import TransactionType


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserLogin(SQLModel):
    username: str
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    is_active: bool


class PasswordChange(SQLModel):
    old_password: str
    new_password: str


class Token(SQLModel):
    access_token: str
    token_type: str


class CategoryDefault(SQLModel):
    title: str
    description: str
    monthly_limit: float


class CategoryRead(CategoryDefault):
    id: int
    user_id: int


class TagDefault(SQLModel):
    name: str
    description: str


class TagRead(TagDefault):
    id: int
    user_id: int


class TransactionDefault(SQLModel):
    transaction_type: TransactionType
    title: str
    amount: float
    operation_date: date
    description: Optional[str] = None
    category_id: Optional[int] = None


class TransactionRead(TransactionDefault):
    id: int
    user_id: int
    category: Optional[CategoryRead] = None
    tags: List[TagRead] = Field(default_factory=list)


class TransactionTagLinkDefault(SQLModel):
    transaction_id: int
    tag_id: int
    importance_level: Optional[int] = None


class TransactionTagLinkRead(TransactionTagLinkDefault):
    pass


class BudgetDefault(SQLModel):
    title: str
    amount: float
    period_start: date
    period_end: date
    category_id: Optional[int] = None


class BudgetRead(BudgetDefault):
    id: int
    user_id: int
    category: Optional[CategoryRead] = None


class GoalDefault(SQLModel):
    title: str
    target_amount: float
    current_amount: float = 0
    deadline: Optional[date] = None
    is_completed: bool = False


class GoalRead(GoalDefault):
    id: int
    user_id: int


class NotificationDefault(SQLModel):
    title: str
    message: str
    is_read: bool = False


class NotificationRead(NotificationDefault):
    id: int
    user_id: int
    created_at: datetime


class FinanceReport(SQLModel):
    total_income: float
    total_expense: float
    balance: float
    budgets_count: int
    goals_count: int
    unread_notifications_count: int


class UserResponse(TypedDict):
    status: int
    data: UserRead


class CategoryResponse(TypedDict):
    status: int
    data: CategoryRead


class TagResponse(TypedDict):
    status: int
    data: TagRead


class TransactionResponse(TypedDict):
    status: int
    data: TransactionRead


class BudgetResponse(TypedDict):
    status: int
    data: BudgetRead


class GoalResponse(TypedDict):
    status: int
    data: GoalRead


class NotificationResponse(TypedDict):
    status: int
    data: NotificationRead


class TransactionTagLinkResponse(TypedDict):
    status: int
    data: TransactionTagLinkRead
