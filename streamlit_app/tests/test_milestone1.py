import csv
from modules.module2_intelligence import get_status


def calculate_expected_status(score):
    if score >= 90:
        return "Hot"
    elif score >= 75:
        return "Warm"
    return "Cold"


def test_sample_dataset_accuracy():

    total = 0
    correct = 0

    with open(
        "streamlit_app/tests/sample_leads.csv",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            total += 1

            expected_score = int(row["Expected Score"])

            expected_status = calculate_expected_status(expected_score)

            predicted_status = get_status(expected_score)

            if predicted_status == expected_status:
                correct += 1

    accuracy = (correct / total) * 100

    print(f"\nAccuracy = {accuracy}%")

    assert accuracy >= 95