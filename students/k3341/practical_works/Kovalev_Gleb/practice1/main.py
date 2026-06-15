from typing import List

from fastapi import FastAPI, HTTPException

from models import (
    Category,
    CategoryResponse,
    Tag,
    TagResponse,
    Transaction,
    TransactionResponse,
    TransactionType,
)

app = FastAPI(
    title="Personal Finance API. Practice 1.1",
    description="Temporary in-memory CRUD API for income and expense tracking.",
)


temp_categories = [
    Category(
        id=1,
        title="Salary",
        description="Main monthly income from work",
        monthly_limit=0,
    ),
    Category(
        id=2,
        title="Food",
        description="Groceries, cafes and other food expenses",
        monthly_limit=30000,
    ),
    Category(
        id=3,
        title="Transport",
        description="Taxi, metro, fuel and other transport expenses",
        monthly_limit=12000,
    ),
]

temp_tags = [
    Tag(id=1, name="regular", description="Repeating planned transaction"),
    Tag(id=2, name="card", description="Paid by bank card"),
    Tag(id=3, name="cash", description="Paid by cash"),
]

temp_transactions = [
    Transaction(
        id=1,
        transaction_type=TransactionType.income,
        title="June salary",
        amount=150000,
        category=temp_categories[0],
        tags=[temp_tags[0], temp_tags[1]],
    ),
    Transaction(
        id=2,
        transaction_type=TransactionType.expense,
        title="Weekly groceries",
        amount=6200,
        category=temp_categories[1],
        tags=[temp_tags[1]],
    ),
    Transaction(
        id=3,
        transaction_type=TransactionType.expense,
        title="Taxi to university",
        amount=850,
        category=temp_categories[2],
        tags=[temp_tags[2]],
    ),
]


@app.get("/")
def hello() -> str:
    return "Hello, personal finance user!"


@app.get("/transactions_list")
def transactions_list() -> List[Transaction]:
    return temp_transactions


@app.get("/transaction/{transaction_id}")
def transaction_get(transaction_id: int) -> Transaction:
    for transaction in temp_transactions:
        if transaction.id == transaction_id:
            return transaction
    raise HTTPException(status_code=404, detail="Transaction not found")


@app.post("/transaction")
def transaction_create(transaction: Transaction) -> TransactionResponse:
    temp_transactions.append(transaction)
    return {"status": 200, "data": transaction}


@app.delete("/transaction/delete{transaction_id}")
def transaction_delete(transaction_id: int) -> dict:
    for index, transaction in enumerate(temp_transactions):
        if transaction.id == transaction_id:
            temp_transactions.pop(index)
            return {"status": 201, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Transaction not found")


@app.put("/transaction{transaction_id}")
def transaction_update(transaction_id: int, transaction: Transaction) -> List[Transaction]:
    for index, current_transaction in enumerate(temp_transactions):
        if current_transaction.id == transaction_id:
            temp_transactions[index] = transaction
            return temp_transactions
    raise HTTPException(status_code=404, detail="Transaction not found")


@app.get("/categories_list")
def categories_list() -> List[Category]:
    return temp_categories


@app.get("/category/{category_id}")
def category_get(category_id: int) -> Category:
    for category in temp_categories:
        if category.id == category_id:
            return category
    raise HTTPException(status_code=404, detail="Category not found")


@app.post("/category")
def category_create(category: Category) -> CategoryResponse:
    temp_categories.append(category)
    return {"status": 200, "data": category}


@app.delete("/category/delete{category_id}")
def category_delete(category_id: int) -> dict:
    for index, category in enumerate(temp_categories):
        if category.id == category_id:
            temp_categories.pop(index)
            return {"status": 201, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Category not found")


@app.put("/category{category_id}")
def category_update(category_id: int, category: Category) -> List[Category]:
    for index, current_category in enumerate(temp_categories):
        if current_category.id == category_id:
            temp_categories[index] = category
            return temp_categories
    raise HTTPException(status_code=404, detail="Category not found")


@app.get("/tags_list")
def tags_list() -> List[Tag]:
    return temp_tags


@app.get("/tag/{tag_id}")
def tag_get(tag_id: int) -> Tag:
    for tag in temp_tags:
        if tag.id == tag_id:
            return tag
    raise HTTPException(status_code=404, detail="Tag not found")


@app.post("/tag")
def tag_create(tag: Tag) -> TagResponse:
    temp_tags.append(tag)
    return {"status": 200, "data": tag}


@app.delete("/tag/delete{tag_id}")
def tag_delete(tag_id: int) -> dict:
    for index, tag in enumerate(temp_tags):
        if tag.id == tag_id:
            temp_tags.pop(index)
            return {"status": 201, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Tag not found")


@app.put("/tag{tag_id}")
def tag_update(tag_id: int, tag: Tag) -> List[Tag]:
    for index, current_tag in enumerate(temp_tags):
        if current_tag.id == tag_id:
            temp_tags[index] = tag
            return temp_tags
    raise HTTPException(status_code=404, detail="Tag not found")
