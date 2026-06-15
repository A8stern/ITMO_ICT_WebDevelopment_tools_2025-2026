def test_register_login_and_me(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "demo",
            "email": "demo@example.com",
            "password": "demo12345",
        },
    )

    assert register_response.status_code == 200
    assert register_response.json()["data"]["username"] == "demo"

    login_response = client.post(
        "/auth/login",
        json={
            "username": "demo",
            "password": "demo12345",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "demo@example.com"


def test_change_password(client, auth_headers):
    response = client.patch(
        "/auth/change_password",
        headers=auth_headers,
        json={
            "old_password": "test12345",
            "new_password": "new12345",
        },
    )

    assert response.status_code == 200
    assert response.json()["ok"] is True

    login_response = client.post(
        "/auth/login",
        json={
            "username": "tester",
            "password": "new12345",
        },
    )

    assert login_response.status_code == 200


def test_users_list_and_duplicate_registration(client, auth_headers):
    users_response = client.get("/auth/users", headers=auth_headers)

    assert users_response.status_code == 200
    assert users_response.json()[0]["username"] == "tester"

    duplicate_response = client.post(
        "/auth/register",
        json={
            "username": "tester",
            "email": "other@example.com",
            "password": "test12345",
        },
    )

    assert duplicate_response.status_code == 400
