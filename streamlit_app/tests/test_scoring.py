from modules.module2_intelligence import (
    get_status,
    analyze_and_score_lead
)


def test_hot_status():
    assert get_status(95) == "Hot"


def test_warm_status():
    assert get_status(80) == "Warm"


def test_cold_status():
    assert get_status(50) == "Cold"


def test_ai_scoring():

    lead = {
        "company": "Google",
        "industry": "Technology",
        "location": "California",
        "website": "https://google.com",
        "contact": "Sundar Pichai",
        "designation": "CEO",
        "notes": "Fortune 500 company"
    }

    result = analyze_and_score_lead(lead)

    assert "analysis" in result
    assert "score" in result
    assert "status" in result

    assert isinstance(result["score"], int)
    assert 0 <= result["score"] <= 100

    if result["score"] >= 90:
        assert result["status"] == "Hot"
    elif result["score"] >= 75:
        assert result["status"] == "Warm"
    else:
        assert result["status"] == "Cold"