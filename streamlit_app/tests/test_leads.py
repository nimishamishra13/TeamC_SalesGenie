from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_lead():

    response = client.post(
        "/leads/",
        json={
            "company": "Google",
            "contact": "John",
            "designation": "Manager",
            "email": "john@test.com",
            "phone": "9876543210",
            "website": "google.com",
            "location": "Delhi",
            "industry": "IT",
            "score": 80,
            "status": "Warm",
            "notes": "Test Lead"
        }
    )

    assert response.status_code == 200


def test_get_all_leads():

    response = client.get("/leads/")

    assert response.status_code == 200

    assert isinstance(response.json(), list)


def test_get_single_lead():

    response = client.get("/leads/1")

    assert response.status_code in [200,404]


def test_update_lead():

    response = client.put(
        "/leads/1",
        json={
            "company":"Google Updated",
            "contact":"John",
            "designation":"Manager",
            "email":"john@test.com",
            "phone":"9999999999",
            "website":"google.com",
            "location":"Delhi",
            "industry":"IT",
            "score":95,
            "status":"Hot",
            "notes":"Updated"
        }
    )

    assert response.status_code in [200,404]


def test_delete_lead():

    response = client.delete("/leads/1")

    assert response.status_code in [200,404]