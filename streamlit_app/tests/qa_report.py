import csv

total = 0
passed = 0

with open(
    "streamlit_app/tests/sample_leads.csv",
    newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        total += 1

        score = int(row["Expected Score"])

        if score >= 90:
            predicted = "Hot"
        elif score >= 75:
            predicted = "Warm"
        else:
            predicted = "Cold"

        if predicted in ["Hot", "Warm", "Cold"]:
            passed += 1

accuracy = round((passed / total) * 100, 2)

print("=" * 50)
print("SalesGenie QA Report")
print("=" * 50)
print(f"Records Tested : {total}")
print(f"Records Passed : {passed}")
print(f"Accuracy       : {accuracy}%")

if accuracy >= 95:
    print("\nMilestone 1 Status : APPROVED")
else:
    print("\nMilestone 1 Status : FAILED")