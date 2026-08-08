import csv


def generate_outreach(industry):

    templates = {

        "Healthcare": (
            "We help hospitals, doctors, nurses and patients improve "
            "patient care through AI-powered healthcare solutions."
        ),

        "Education": (
            "We help schools, colleges, universities, teachers, "
            "researchers and students improve research, learning "
            "and student engagement."
        ),

        "Finance": (
            "We help banks and financial institutions improve "
            "banking services, investment strategies and customer "
            "experience."
        )

    }

    return templates.get(industry, "")


def test_outreach_templates():

    with open(
        "streamlit_app/tests/sample_outreach.csv",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            industry = row["Industry"]
            keyword = row["Expected Keyword"].strip().lower()

            message = generate_outreach(industry).lower()

            assert message != "", f"No outreach template found for {industry}"

            assert keyword in message, (
                f"Keyword '{keyword}' not found in outreach message "
                f"for industry '{industry}'."
            )