from fastapi import APIRouter   

router = APIRouter()            
from fastapi import Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import csv
import io
import re

from database.connection import get_db
from database.models import Lead


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


@router.post("/leads/")
def create_lead(data: dict, db: Session = Depends(get_db)):

    if not data.get("email") or not is_valid_email(data.get("email")):
        raise HTTPException(status_code=400, detail="Invalid email")

    existing = db.query(Lead).filter(Lead.email == data.get("email")).first()
    if existing:
        raise HTTPException(status_code=400, detail="Lead already exists")

    new_lead = Lead(**data)

    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return {"message": "Lead created", "lead": new_lead}


@router.post("/leads/upload-csv")
def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):

    content = file.file.read().decode("utf-8")

    if not content.strip():
        raise HTTPException(status_code=400, detail="CSV file is empty")

    reader = csv.DictReader(io.StringIO(content))

    inserted = 0
    duplicates = 0
    invalid = 0

    for row in reader:
        email = row.get("email")

        if not email or not is_valid_email(email):
            invalid += 1
            continue

        existing = db.query(Lead).filter(Lead.email == email).first()
        if existing:
            duplicates += 1
            continue

        new_lead = Lead(
            name=row.get("name"),
            email=email,
            company=row.get("company"),
            status=row.get("status"),
            notes=row.get("notes"),
        )

        db.add(new_lead)
        inserted += 1

    db.commit()

    return {
        "inserted": inserted,
        "duplicates": duplicates,
        "invalid": invalid
    }


@router.get("/leads/")
def get_leads(db: Session = Depends(get_db)):
    return db.query(Lead).all()


@router.put("/leads/{lead_id}")
def update_lead(lead_id: int, data: dict, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Not found")

    for key, value in data.items():
        setattr(lead, key, value)

    db.commit()
    db.refresh(lead)

    return {"message": "Updated", "lead": lead}


@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(lead)
    db.commit()

    return {"message": "Deleted"}