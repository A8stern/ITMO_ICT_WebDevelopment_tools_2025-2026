from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.dependencies import get_current_user
from app.models import Budget, Category, Goal, Notification, Tag, Transaction, TransactionTagLink, TransactionType, User
from app.schemas import (
    BudgetDefault,
    BudgetRead,
    BudgetResponse,
    CategoryDefault,
    CategoryRead,
    CategoryResponse,
    FinanceReport,
    GoalDefault,
    GoalRead,
    GoalResponse,
    NotificationDefault,
    NotificationRead,
    NotificationResponse,
    TagDefault,
    TagRead,
    TagResponse,
    TransactionDefault,
    TransactionRead,
    TransactionResponse,
    TransactionTagLinkDefault,
    TransactionTagLinkRead,
    TransactionTagLinkResponse,
)

router = APIRouter(tags=["finance"])


def get_owned_category(category_id: int, user_id: int, session: Session) -> Category:
    category = session.get(Category, category_id)
    if not category or category.user_id != user_id:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def get_owned_tag(tag_id: int, user_id: int, session: Session) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != user_id:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


def get_owned_transaction(transaction_id: int, user_id: int, session: Session) -> Transaction:
    transaction = session.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


def get_owned_budget(budget_id: int, user_id: int, session: Session) -> Budget:
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != user_id:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


def get_owned_goal(goal_id: int, user_id: int, session: Session) -> Goal:
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != user_id:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


def get_owned_notification(notification_id: int, user_id: int, session: Session) -> Notification:
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != user_id:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.get("/categories_list", response_model=List[CategoryRead])
def categories_list(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Category]:
    return session.exec(select(Category).where(Category.user_id == current_user.id)).all()


@router.get("/category/{category_id}", response_model=CategoryRead)
def category_get(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Category:
    return get_owned_category(category_id, current_user.id, session)


@router.post("/category")
def category_create(
    category: CategoryDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> CategoryResponse:
    db_category = Category.model_validate(category, update={"user_id": current_user.id})
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return {"status": 200, "data": db_category}


@router.patch("/category{category_id}", response_model=CategoryRead)
def category_update(
    category_id: int,
    category: CategoryDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Category:
    db_category = get_owned_category(category_id, current_user.id, session)
    category_data = category.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.delete("/category/delete{category_id}")
def category_delete(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    category = get_owned_category(category_id, current_user.id, session)
    session.delete(category)
    session.commit()
    return {"ok": True}


@router.get("/tags_list", response_model=List[TagRead])
def tags_list(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Tag]:
    return session.exec(select(Tag).where(Tag.user_id == current_user.id)).all()


@router.get("/tag/{tag_id}", response_model=TagRead)
def tag_get(
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Tag:
    return get_owned_tag(tag_id, current_user.id, session)


@router.post("/tag")
def tag_create(
    tag: TagDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TagResponse:
    db_tag = Tag.model_validate(tag, update={"user_id": current_user.id})
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return {"status": 200, "data": db_tag}


@router.patch("/tag{tag_id}", response_model=TagRead)
def tag_update(
    tag_id: int,
    tag: TagDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Tag:
    db_tag = get_owned_tag(tag_id, current_user.id, session)
    tag_data = tag.model_dump(exclude_unset=True)
    for key, value in tag_data.items():
        setattr(db_tag, key, value)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@router.delete("/tag/delete{tag_id}")
def tag_delete(
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    tag = get_owned_tag(tag_id, current_user.id, session)
    session.delete(tag)
    session.commit()
    return {"ok": True}


@router.get("/transactions_list", response_model=List[TransactionRead])
def transactions_list(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Transaction]:
    return session.exec(select(Transaction).where(Transaction.user_id == current_user.id)).all()


@router.get("/transaction/{transaction_id}", response_model=TransactionRead)
def transaction_get(
    transaction_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    return get_owned_transaction(transaction_id, current_user.id, session)


@router.post("/transaction")
def transaction_create(
    transaction: TransactionDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    if transaction.category_id is not None:
        get_owned_category(transaction.category_id, current_user.id, session)
    db_transaction = Transaction.model_validate(transaction, update={"user_id": current_user.id})
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return {"status": 200, "data": db_transaction}


@router.patch("/transaction{transaction_id}", response_model=TransactionRead)
def transaction_update(
    transaction_id: int,
    transaction: TransactionDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    db_transaction = get_owned_transaction(transaction_id, current_user.id, session)
    if transaction.category_id is not None:
        get_owned_category(transaction.category_id, current_user.id, session)
    transaction_data = transaction.model_dump(exclude_unset=True)
    for key, value in transaction_data.items():
        setattr(db_transaction, key, value)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


@router.delete("/transaction/delete{transaction_id}")
def transaction_delete(
    transaction_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    transaction = get_owned_transaction(transaction_id, current_user.id, session)
    session.delete(transaction)
    session.commit()
    return {"ok": True}


@router.post("/transaction_tag")
def transaction_tag_create(
    transaction_tag: TransactionTagLinkDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TransactionTagLinkResponse:
    get_owned_transaction(transaction_tag.transaction_id, current_user.id, session)
    get_owned_tag(transaction_tag.tag_id, current_user.id, session)
    existing_link = session.exec(
        select(TransactionTagLink)
        .where(TransactionTagLink.transaction_id == transaction_tag.transaction_id)
        .where(TransactionTagLink.tag_id == transaction_tag.tag_id)
    ).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="Transaction tag link already exists")
    db_link = TransactionTagLink.model_validate(transaction_tag)
    session.add(db_link)
    session.commit()
    session.refresh(db_link)
    return {"status": 200, "data": db_link}


@router.get("/transaction_tags_list", response_model=List[TransactionTagLinkRead])
def transaction_tags_list(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[TransactionTagLink]:
    user_transactions = session.exec(
        select(Transaction.id).where(Transaction.user_id == current_user.id)
    ).all()
    return session.exec(
        select(TransactionTagLink).where(TransactionTagLink.transaction_id.in_(user_transactions))
    ).all()


@router.patch("/transaction/{transaction_id}/tag/{tag_id}", response_model=TransactionTagLinkRead)
def transaction_tag_update(
    transaction_id: int,
    tag_id: int,
    transaction_tag: TransactionTagLinkDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TransactionTagLink:
    get_owned_transaction(transaction_id, current_user.id, session)
    get_owned_tag(tag_id, current_user.id, session)
    link = session.exec(
        select(TransactionTagLink)
        .where(TransactionTagLink.transaction_id == transaction_id)
        .where(TransactionTagLink.tag_id == tag_id)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Transaction tag link not found")
    link.importance_level = transaction_tag.importance_level
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


@router.delete("/transaction/{transaction_id}/tag/{tag_id}")
def transaction_tag_delete(
    transaction_id: int,
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    get_owned_transaction(transaction_id, current_user.id, session)
    get_owned_tag(tag_id, current_user.id, session)
    link = session.exec(
        select(TransactionTagLink)
        .where(TransactionTagLink.transaction_id == transaction_id)
        .where(TransactionTagLink.tag_id == tag_id)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Transaction tag link not found")
    session.delete(link)
    session.commit()
    return {"ok": True}


@router.get("/budgets_list", response_model=List[BudgetRead])
def budgets_list(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Budget]:
    return session.exec(select(Budget).where(Budget.user_id == current_user.id)).all()


@router.get("/budget/{budget_id}", response_model=BudgetRead)
def budget_get(
    budget_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Budget:
    return get_owned_budget(budget_id, current_user.id, session)


@router.post("/budget")
def budget_create(
    budget: BudgetDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BudgetResponse:
    if budget.category_id is not None:
        get_owned_category(budget.category_id, current_user.id, session)
    db_budget = Budget.model_validate(budget, update={"user_id": current_user.id})
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return {"status": 200, "data": db_budget}


@router.patch("/budget{budget_id}", response_model=BudgetRead)
def budget_update(
    budget_id: int,
    budget: BudgetDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Budget:
    db_budget = get_owned_budget(budget_id, current_user.id, session)
    if budget.category_id is not None:
        get_owned_category(budget.category_id, current_user.id, session)
    budget_data = budget.model_dump(exclude_unset=True)
    for key, value in budget_data.items():
        setattr(db_budget, key, value)
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return db_budget


@router.delete("/budget/delete{budget_id}")
def budget_delete(
    budget_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    budget = get_owned_budget(budget_id, current_user.id, session)
    session.delete(budget)
    session.commit()
    return {"ok": True}


@router.get("/goals_list", response_model=List[GoalRead])
def goals_list(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Goal]:
    return session.exec(select(Goal).where(Goal.user_id == current_user.id)).all()


@router.get("/goal/{goal_id}", response_model=GoalRead)
def goal_get(
    goal_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Goal:
    return get_owned_goal(goal_id, current_user.id, session)


@router.post("/goal")
def goal_create(
    goal: GoalDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> GoalResponse:
    db_goal = Goal.model_validate(goal, update={"user_id": current_user.id})
    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return {"status": 200, "data": db_goal}


@router.patch("/goal{goal_id}", response_model=GoalRead)
def goal_update(
    goal_id: int,
    goal: GoalDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Goal:
    db_goal = get_owned_goal(goal_id, current_user.id, session)
    goal_data = goal.model_dump(exclude_unset=True)
    for key, value in goal_data.items():
        setattr(db_goal, key, value)
    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return db_goal


@router.delete("/goal/delete{goal_id}")
def goal_delete(
    goal_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    goal = get_owned_goal(goal_id, current_user.id, session)
    session.delete(goal)
    session.commit()
    return {"ok": True}


@router.get("/notifications_list", response_model=List[NotificationRead])
def notifications_list(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Notification]:
    return session.exec(select(Notification).where(Notification.user_id == current_user.id)).all()


@router.get("/notification/{notification_id}", response_model=NotificationRead)
def notification_get(
    notification_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Notification:
    return get_owned_notification(notification_id, current_user.id, session)


@router.post("/notification")
def notification_create(
    notification: NotificationDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    db_notification = Notification.model_validate(notification, update={"user_id": current_user.id})
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)
    return {"status": 200, "data": db_notification}


@router.patch("/notification{notification_id}", response_model=NotificationRead)
def notification_update(
    notification_id: int,
    notification: NotificationDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Notification:
    db_notification = get_owned_notification(notification_id, current_user.id, session)
    notification_data = notification.model_dump(exclude_unset=True)
    for key, value in notification_data.items():
        setattr(db_notification, key, value)
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)
    return db_notification


@router.delete("/notification/delete{notification_id}")
def notification_delete(
    notification_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    notification = get_owned_notification(notification_id, current_user.id, session)
    session.delete(notification)
    session.commit()
    return {"ok": True}


@router.get("/report", response_model=FinanceReport)
def report(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> FinanceReport:
    transactions = session.exec(select(Transaction).where(Transaction.user_id == current_user.id)).all()
    budgets = session.exec(select(Budget).where(Budget.user_id == current_user.id)).all()
    goals = session.exec(select(Goal).where(Goal.user_id == current_user.id)).all()
    notifications = session.exec(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)
    ).all()
    total_income = sum(item.amount for item in transactions if item.transaction_type == TransactionType.income)
    total_expense = sum(item.amount for item in transactions if item.transaction_type == TransactionType.expense)
    return FinanceReport(
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        budgets_count=len(budgets),
        goals_count=len(goals),
        unread_notifications_count=len(notifications),
    )
