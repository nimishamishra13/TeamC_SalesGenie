from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_create_lead_sync():

    lead = {
        "company": "QA CRM Company",
        "industry": "Technology",
        "location": "India",
        "website": "https://example.com",
        "contact": "QA Tester",
        "designation": "Manager",
        "notes": "CRM synchronization test"
    }

    response = client.post(
        "/leads/",
        json=lead
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data is not None


def test_read_leads_after_creation():

    response = client.get("/leads/")

    assert response.status_code == 200

    leads = response.json()

    assert isinstance(leads, list)


def test_lead_data_is_preserved():

    response = client.get("/leads/")

    assert response.status_code == 200

    leads = response.json()

    qa_leads = [
        lead
        for lead in leads
        if lead.get("company") == "QA CRM Company"
    ]

    assert len(qa_leads) >= 1

    lead = qa_leads[0]

    assert lead.get("company") == "QA CRM Company"
    assert lead.get("industry") == "Technology"
    assert lead.get("location") == "India"


def test_update_synced_lead():

    response = client.get("/leads/")

    assert response.status_code == 200

    leads = response.json()

    qa_leads = [
        lead
        for lead in leads
        if lead.get("company") == "QA CRM Company"
    ]

    assert len(qa_leads) >= 1

    lead_id = qa_leads[0]["id"]

    update_response = client.put(
        f"/leads/{lead_id}",
        json={
            "company": "QA CRM Company Updated",
            "industry": "Technology",
            "location": "India",
            "website": "https://example.com",
            "contact": "QA Tester",
            "designation": "Senior Manager",
            "notes": "Updated CRM synchronization test"
        }
    )

    assert update_response.status_code in (200, 204)


def test_updated_data_is_synced():

    response = client.get("/leads/")

    assert response.status_code == 200

    leads = response.json()

    updated_leads = [
        lead
        for lead in leads
        if lead.get("company") == "QA CRM Company Updated"
    ]

    assert len(updated_leads) >= 1

    lead = updated_leads[0]

    assert lead.get("designation") == "Senior Manager"
    assert lead.get("notes") == "Updated CRM synchronization test"