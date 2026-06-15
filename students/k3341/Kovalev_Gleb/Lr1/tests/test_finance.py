def create_category(client, auth_headers, title="Food"):
    category_response = client.post(
        "/category",
        headers=auth_headers,
        json={
            "title": title,
            "description": "Groceries and cafes",
            "monthly_limit": 30000,
        },
    )
    assert category_response.status_code == 200
    return category_response.json()["data"]["id"]


def create_tag(client, auth_headers, name="card"):
    tag_response = client.post(
        "/tag",
        headers=auth_headers,
        json={
            "name": name,
            "description": "Paid by bank card",
        },
    )
    assert tag_response.status_code == 200
    return tag_response.json()["data"]["id"]


def create_transaction(client, auth_headers, category_id, title="Groceries", amount=4500, transaction_type="expense"):
    transaction_response = client.post(
        "/transaction",
        headers=auth_headers,
        json={
            "transaction_type": transaction_type,
            "title": title,
            "amount": amount,
            "operation_date": "2026-06-14",
            "description": title,
            "category_id": category_id,
        },
    )
    assert transaction_response.status_code == 200
    return transaction_response.json()["data"]["id"]


def test_full_finance_flow(client, auth_headers):
    category_id = create_category(client, auth_headers)
    tag_id = create_tag(client, auth_headers)
    transaction_id = create_transaction(client, auth_headers, category_id)

    link_response = client.post(
        "/transaction_tag",
        headers=auth_headers,
        json={
            "transaction_id": transaction_id,
            "tag_id": tag_id,
            "importance_level": 5,
        },
    )

    assert link_response.status_code == 200

    links_response = client.get("/transaction_tags_list", headers=auth_headers)

    assert links_response.status_code == 200
    assert links_response.json()[0]["importance_level"] == 5

    link_update_response = client.patch(
        f"/transaction/{transaction_id}/tag/{tag_id}",
        headers=auth_headers,
        json={
            "transaction_id": transaction_id,
            "tag_id": tag_id,
            "importance_level": 9,
        },
    )

    assert link_update_response.status_code == 200
    assert link_update_response.json()["importance_level"] == 9

    budget_response = client.post(
        "/budget",
        headers=auth_headers,
        json={
            "title": "Food budget",
            "amount": 30000,
            "period_start": "2026-06-01",
            "period_end": "2026-06-30",
            "category_id": category_id,
        },
    )

    assert budget_response.status_code == 200

    goal_response = client.post(
        "/goal",
        headers=auth_headers,
        json={
            "title": "Emergency fund",
            "target_amount": 200000,
            "current_amount": 25000,
            "deadline": "2026-12-31",
            "is_completed": False,
        },
    )

    assert goal_response.status_code == 200

    notification_response = client.post(
        "/notification",
        headers=auth_headers,
        json={
            "title": "Budget warning",
            "message": "Food budget is almost exceeded",
            "is_read": False,
        },
    )

    assert notification_response.status_code == 200

    get_transaction_response = client.get(
        f"/transaction/{transaction_id}",
        headers=auth_headers,
    )
    transaction_data = get_transaction_response.json()

    assert get_transaction_response.status_code == 200
    assert transaction_data["category"]["title"] == "Food"
    assert transaction_data["tags"][0]["name"] == "card"

    report_response = client.get("/report", headers=auth_headers)
    report = report_response.json()

    assert report_response.status_code == 200
    assert report["total_expense"] == 4500
    assert report["budgets_count"] == 1
    assert report["goals_count"] == 1
    assert report["unread_notifications_count"] == 1


def test_category_crud_endpoints(client, auth_headers):
    category_id = create_category(client, auth_headers)

    list_response = client.get("/categories_list", headers=auth_headers)
    get_response = client.get(f"/category/{category_id}", headers=auth_headers)
    update_response = client.patch(
        f"/category{category_id}",
        headers=auth_headers,
        json={
            "title": "Food updated",
            "description": "Updated",
            "monthly_limit": 35000,
        },
    )
    delete_response = client.delete(f"/category/delete{category_id}", headers=auth_headers)
    missing_response = client.get(f"/category/{category_id}", headers=auth_headers)

    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Food updated"
    assert delete_response.status_code == 200
    assert missing_response.status_code == 404


def test_tag_crud_endpoints(client, auth_headers):
    tag_id = create_tag(client, auth_headers)

    list_response = client.get("/tags_list", headers=auth_headers)
    get_response = client.get(f"/tag/{tag_id}", headers=auth_headers)
    update_response = client.patch(
        f"/tag{tag_id}",
        headers=auth_headers,
        json={
            "name": "cash",
            "description": "Paid by cash",
        },
    )
    delete_response = client.delete(f"/tag/delete{tag_id}", headers=auth_headers)
    missing_response = client.get(f"/tag/{tag_id}", headers=auth_headers)

    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "cash"
    assert delete_response.status_code == 200
    assert missing_response.status_code == 404


def test_transaction_crud_endpoints(client, auth_headers):
    category_id = create_category(client, auth_headers)
    transaction_id = create_transaction(client, auth_headers, category_id)

    list_response = client.get("/transactions_list", headers=auth_headers)
    get_response = client.get(f"/transaction/{transaction_id}", headers=auth_headers)
    update_response = client.patch(
        f"/transaction{transaction_id}",
        headers=auth_headers,
        json={
            "transaction_type": "income",
            "title": "Salary",
            "amount": 150000,
            "operation_date": "2026-06-14",
            "description": "June salary",
            "category_id": category_id,
        },
    )
    delete_response = client.delete(f"/transaction/delete{transaction_id}", headers=auth_headers)
    missing_response = client.get(f"/transaction/{transaction_id}", headers=auth_headers)

    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert update_response.json()["transaction_type"] == "income"
    assert delete_response.status_code == 200
    assert missing_response.status_code == 404


def test_transaction_tag_crud_endpoints(client, auth_headers):
    category_id = create_category(client, auth_headers)
    tag_id = create_tag(client, auth_headers)
    transaction_id = create_transaction(client, auth_headers, category_id)

    create_response = client.post(
        "/transaction_tag",
        headers=auth_headers,
        json={
            "transaction_id": transaction_id,
            "tag_id": tag_id,
            "importance_level": 3,
        },
    )
    list_response = client.get("/transaction_tags_list", headers=auth_headers)
    update_response = client.patch(
        f"/transaction/{transaction_id}/tag/{tag_id}",
        headers=auth_headers,
        json={
            "transaction_id": transaction_id,
            "tag_id": tag_id,
            "importance_level": 7,
        },
    )
    delete_response = client.delete(f"/transaction/{transaction_id}/tag/{tag_id}", headers=auth_headers)
    missing_delete_response = client.delete(f"/transaction/{transaction_id}/tag/{tag_id}", headers=auth_headers)

    assert create_response.status_code == 200
    assert list_response.status_code == 200
    assert update_response.status_code == 200
    assert update_response.json()["importance_level"] == 7
    assert delete_response.status_code == 200
    assert missing_delete_response.status_code == 404


def test_budget_crud_endpoints(client, auth_headers):
    category_id = create_category(client, auth_headers)
    create_response = client.post(
        "/budget",
        headers=auth_headers,
        json={
            "title": "Food budget",
            "amount": 30000,
            "period_start": "2026-06-01",
            "period_end": "2026-06-30",
            "category_id": category_id,
        },
    )
    budget_id = create_response.json()["data"]["id"]

    list_response = client.get("/budgets_list", headers=auth_headers)
    get_response = client.get(f"/budget/{budget_id}", headers=auth_headers)
    update_response = client.patch(
        f"/budget{budget_id}",
        headers=auth_headers,
        json={
            "title": "Updated budget",
            "amount": 40000,
            "period_start": "2026-06-01",
            "period_end": "2026-06-30",
            "category_id": category_id,
        },
    )
    delete_response = client.delete(f"/budget/delete{budget_id}", headers=auth_headers)
    missing_response = client.get(f"/budget/{budget_id}", headers=auth_headers)

    assert create_response.status_code == 200
    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated budget"
    assert delete_response.status_code == 200
    assert missing_response.status_code == 404


def test_goal_crud_endpoints(client, auth_headers):
    create_response = client.post(
        "/goal",
        headers=auth_headers,
        json={
            "title": "Emergency fund",
            "target_amount": 200000,
            "current_amount": 25000,
            "deadline": "2026-12-31",
            "is_completed": False,
        },
    )
    goal_id = create_response.json()["data"]["id"]

    list_response = client.get("/goals_list", headers=auth_headers)
    get_response = client.get(f"/goal/{goal_id}", headers=auth_headers)
    update_response = client.patch(
        f"/goal{goal_id}",
        headers=auth_headers,
        json={
            "title": "Updated fund",
            "target_amount": 250000,
            "current_amount": 50000,
            "deadline": "2026-12-31",
            "is_completed": False,
        },
    )
    delete_response = client.delete(f"/goal/delete{goal_id}", headers=auth_headers)
    missing_response = client.get(f"/goal/{goal_id}", headers=auth_headers)

    assert create_response.status_code == 200
    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated fund"
    assert delete_response.status_code == 200
    assert missing_response.status_code == 404


def test_notification_crud_endpoints(client, auth_headers):
    create_response = client.post(
        "/notification",
        headers=auth_headers,
        json={
            "title": "Budget warning",
            "message": "Food budget is almost exceeded",
            "is_read": False,
        },
    )
    notification_id = create_response.json()["data"]["id"]

    list_response = client.get("/notifications_list", headers=auth_headers)
    get_response = client.get(f"/notification/{notification_id}", headers=auth_headers)
    update_response = client.patch(
        f"/notification{notification_id}",
        headers=auth_headers,
        json={
            "title": "Read warning",
            "message": "Budget checked",
            "is_read": True,
        },
    )
    delete_response = client.delete(f"/notification/delete{notification_id}", headers=auth_headers)
    missing_response = client.get(f"/notification/{notification_id}", headers=auth_headers)

    assert create_response.status_code == 200
    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert update_response.json()["is_read"] is True
    assert delete_response.status_code == 200
    assert missing_response.status_code == 404


def test_user_cannot_read_without_token(client):
    response = client.get("/categories_list")

    assert response.status_code == 401
