def test_get_persons_empty(client):
    response = client.get("/api/v1/persons")

    assert response.status_code == 200
    assert response.json() == []


def test_create_person(client):
    person = {
        "name": "Sergei",
        "age": 22,
        "address": "Moscow",
        "work": "searching",
    }

    response = client.post(
        "/api/v1/persons",
        json=person,
    )

    assert response.status_code == 201

    assert response.headers["location"] == "/api/v1/persons/1"

    assert response.content == b""


def test_create_and_get_person(client):
    person = {
        "name": "Sergei",
        "age": 22,
        "address": "Moscow",
        "work": "searching",
    }

    create_response = client.post(
        "/api/v1/persons",
        json=person,
    )

    assert create_response.status_code == 201

    location = create_response.headers["location"]

    response = client.get(location)

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "name": "Sergei",
        "age": 22,
        "address": "Moscow",
        "work": "searching",
    }


def test_get_nonexistent_person(client):
    response = client.get("/api/v1/persons/999")

    assert response.status_code == 404

    assert response.json() == {
        "message": "Пользователь не найден"
    }


def test_create_person_invalid_data(client):
    response = client.post(
        "/api/v1/persons",
        json={
            "age": "not-an-integer",
            "address": "Moscow",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["message"] == "Invalid data"
    assert "errors" in body