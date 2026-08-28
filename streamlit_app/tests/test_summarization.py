from ai.ai_analysis import summarize_lead


def test_summary_is_generated():

    lead = {
        "company": "Google",
        "industry": "Technology",
        "location": "India",
        "contact": "Rahul",
        "designation": "Sales Manager",
        "notes": "Interested in AI solutions and enterprise software."
    }

    summary = summarize_lead(lead)

    assert summary is not None
    assert isinstance(summary, str)
    assert len(summary.strip()) > 20


def test_summary_contains_company():

    lead = {
        "company": "Microsoft",
        "industry": "Technology",
        "location": "India",
        "contact": "Ankit",
        "designation": "Business Manager",
        "notes": "Interested in cloud and AI solutions."
    }

    summary = summarize_lead(lead)

    assert "Microsoft".lower() in summary.lower()


def test_summary_contains_industry():

    lead = {
        "company": "Apollo Hospital",
        "industry": "Healthcare",
        "location": "India",
        "contact": "Dr. Sharma",
        "designation": "Director",
        "notes": "Interested in AI healthcare solutions."
    }

    summary = summarize_lead(lead)

    assert "Healthcare".lower() in summary.lower()


def test_summary_does_not_return_error():

    lead = {
        "company": "Amazon",
        "industry": "Technology",
        "location": "India",
        "contact": "Rohit",
        "designation": "Manager",
        "notes": "Interested in cloud services."
    }

    summary = summarize_lead(lead)

    assert "error" not in summary.lower()
    assert "failed" not in summary.lower()