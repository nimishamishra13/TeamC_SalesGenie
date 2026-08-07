import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

# Load dataset
df = pd.read_csv("dataset/lead_dataset.csv")
print(df["industry"].unique())

# Label Encoders
label_encoders = {}

categorical_columns = [
    "industry",
    "company_size",
    "lead_status"
]

for col in categorical_columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le
print(label_encoders["industry"].classes_)
# Features
X = df.drop("converted", axis=1)

# Target
y = df["converted"]

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train Model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Predictions
predictions = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, predictions)

print(f"\nAccuracy: {accuracy * 100:.2f}%\n")

print(classification_report(y_test, predictions))

# Save model
joblib.dump(model, "model.pkl")
joblib.dump(label_encoders, "label_encoders.pkl")

print("\nModel saved successfully!")
