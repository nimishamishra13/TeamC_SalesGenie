import csv
from modules.module2_intelligence import get_status


def expected_status(score):

    if score >= 90:
        return "Hot"

    elif score >= 75:
        return "Warm"

    return "Cold"


def test_lead_scoring_accuracy():

    total = 0
    correct = 0

    with open(
        "streamlit_app/tests/sample_leads.csv",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            total += 1

            score = int(row["Expected Score"])

            predicted = get_status(score)

            if predicted == expected_status(score):
                correct += 1

    accuracy = (correct / total) * 100

    print(f"\nLead Accuracy : {accuracy}%")

    assert accuracy >= 85