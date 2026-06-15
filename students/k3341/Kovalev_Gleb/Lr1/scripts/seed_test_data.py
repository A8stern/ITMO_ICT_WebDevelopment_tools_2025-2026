import os
import sys
from datetime import date
from pathlib import Path

project_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_dir))

os.environ["DB_ADMIN"] = os.getenv("DB_ADMIN", "sqlite:////private/tmp/finance_lab_frontend.db")
os.environ["JWT_SECRET"] = os.getenv("JWT_SECRET", "frontend-test-secret")
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")

from sqlmodel import Session, SQLModel

from app.auth import hash_password
from app.db import engine
from app.models import Budget, Category, Goal, Notification, Tag, Transaction, TransactionTagLink, TransactionType, User


def seed() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(
            username="demo",
            email="demo@example.com",
            hashed_password=hash_password("demo12345"),
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        food = Category(
            title="Food",
            description="Groceries and cafes",
            monthly_limit=30000,
            user_id=user.id,
        )
        salary = Category(
            title="Salary",
            description="Main income",
            monthly_limit=0,
            user_id=user.id,
        )
        card = Tag(name="card", description="Paid by bank card", user_id=user.id)
        regular = Tag(name="regular", description="Repeating transaction", user_id=user.id)
        session.add(food)
        session.add(salary)
        session.add(card)
        session.add(regular)
        session.commit()
        session.refresh(food)
        session.refresh(salary)
        session.refresh(card)
        session.refresh(regular)

        income = Transaction(
            transaction_type=TransactionType.income,
            title="June salary",
            amount=150000,
            operation_date=date(2026, 6, 14),
            description="Main monthly income",
            user_id=user.id,
            category_id=salary.id,
        )
        expense = Transaction(
            transaction_type=TransactionType.expense,
            title="Groceries",
            amount=4500,
            operation_date=date(2026, 6, 14),
            description="Weekly groceries",
            user_id=user.id,
            category_id=food.id,
        )
        session.add(income)
        session.add(expense)
        session.commit()
        session.refresh(income)
        session.refresh(expense)

        session.add(TransactionTagLink(transaction_id=income.id, tag_id=regular.id, importance_level=4))
        session.add(TransactionTagLink(transaction_id=expense.id, tag_id=card.id, importance_level=8))
        session.add(
            Budget(
                title="Food budget for June",
                amount=30000,
                period_start=date(2026, 6, 1),
                period_end=date(2026, 6, 30),
                user_id=user.id,
                category_id=food.id,
            )
        )
        session.add(
            Goal(
                title="Emergency fund",
                target_amount=200000,
                current_amount=25000,
                deadline=date(2026, 12, 31),
                user_id=user.id,
            )
        )
        session.add(
            Notification(
                title="Budget warning",
                message="Food budget is almost exceeded",
                user_id=user.id,
            )
        )
        session.commit()


if __name__ == "__main__":
    seed()
    print("Seeded demo user: demo / demo12345")
