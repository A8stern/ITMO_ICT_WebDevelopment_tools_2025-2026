def test_frontend_page_is_served(client):
    response = client.get("/app")

    assert response.status_code == 200
    assert "ЛИЧНЫЕ ФИНАНСЫ" in response.text
    assert "/static/styles.css" in response.text
    assert "/static/app.js" in response.text


def test_frontend_static_assets_are_served(client):
    css_response = client.get("/static/styles.css")
    js_response = client.get("/static/app.js")
    root_response = client.get("/")

    assert css_response.status_code == 200
    assert js_response.status_code == 200
    assert root_response.status_code == 200
    assert "Hello, personal finance lab user!" in root_response.text
