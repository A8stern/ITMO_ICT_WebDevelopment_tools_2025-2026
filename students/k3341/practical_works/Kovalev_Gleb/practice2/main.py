from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import select

from connection import get_session, init_db
from models import (
    Category,
    CategoryDefault,
    CategoryRead,
    CategoryResponse,
    Tag,
    TagDefault,
    TagRead,
    TagResponse,
    Transaction,
    TransactionDefault,
    TransactionRead,
    TransactionResponse,
    TransactionTagLink,
)

app = FastAPI(
    title="Personal Finance API. Practice 1.2",
    description="SQLModel CRUD API for income, expenses, categories and tags.",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def hello() -> str:
    return "Hello, personal finance database user!"


@app.get("/transactions_list", response_model=List[TransactionRead])
def transactions_list(session=Depends(get_session)) -> List[Transaction]:
    return session.exec(select(Transaction)).all()


@app.get("/transaction/{transaction_id}", response_model=TransactionRead)
def transaction_get(transaction_id: int, session=Depends(get_session)) -> Transaction:
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/transaction")
def transaction_create(
    transaction: TransactionDefault,
    session=Depends(get_session),
) -> TransactionResponse:
    db_transaction = Transaction.model_validate(transaction)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return {"status": 200, "data": db_transaction}


@app.patch("/transaction{transaction_id}", response_model=TransactionRead)
def transaction_update(
    transaction_id: int,
    transaction: TransactionDefault,
    session=Depends(get_session),
) -> Transaction:
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction_data = transaction.model_dump(exclude_unset=True)
    for key, value in transaction_data.items():
        setattr(db_transaction, key, value)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


@app.delete("/transaction/delete{transaction_id}")
def transaction_delete(transaction_id: int, session=Depends(get_session)) -> dict:
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return {"ok": True}


@app.post("/transaction/{transaction_id}/tag/{tag_id}", response_model=TransactionRead)
def transaction_add_tag(
    transaction_id: int,
    tag_id: int,
    session=Depends(get_session),
) -> Transaction:
    transaction = session.get(Transaction, transaction_id)
    tag = session.get(Tag, tag_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag not in transaction.tags:
        transaction.tags.append(tag)
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
    return transaction


@app.delete("/transaction/{transaction_id}/tag/{tag_id}")
def transaction_remove_tag(
    transaction_id: int,
    tag_id: int,
    session=Depends(get_session),
) -> dict:
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


@app.get("/categories_list", response_model=List[CategoryRead])
def categories_list(session=Depends(get_session)) -> List[Category]:
    return session.exec(select(Category)).all()


@app.get("/category/{category_id}", response_model=CategoryRead)
def category_get(category_id: int, session=Depends(get_session)) -> Category:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.post("/category")
def category_create(
    category: CategoryDefault,
    session=Depends(get_session),
) -> CategoryResponse:
    db_category = Category.model_validate(category)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return {"status": 200, "data": db_category}


@app.patch("/category{category_id}", response_model=CategoryRead)
def category_update(
    category_id: int,
    category: CategoryDefault,
    session=Depends(get_session),
) -> Category:
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    category_data = category.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@app.delete("/category/delete{category_id}")
def category_delete(category_id: int, session=Depends(get_session)) -> dict:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"ok": True}


@app.get("/tags_list", response_model=List[TagRead])
def tags_list(session=Depends(get_session)) -> List[Tag]:
    return session.exec(select(Tag)).all()


@app.get("/tag/{tag_id}", response_model=TagRead)
def tag_get(tag_id: int, session=Depends(get_session)) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@app.post("/tag")
def tag_create(tag: TagDefault, session=Depends(get_session)) -> TagResponse:
    db_tag = Tag.model_validate(tag)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return {"status": 200, "data": db_tag}


@app.patch("/tag{tag_id}", response_model=TagRead)
def tag_update(
    tag_id: int,
    tag: TagDefault,
    session=Depends(get_session),
) -> Tag:
    db_tag = session.get(Tag, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    tag_data = tag.model_dump(exclude_unset=True)
    for key, value in tag_data.items():
        setattr(db_tag, key, value)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@app.delete("/tag/delete{tag_id}")
def tag_delete(tag_id: int, session=Depends(get_session)) -> dict:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(tag)
    session.commit()
    return {"ok": True}
