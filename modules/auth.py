from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import bcrypt

from database.connection import SessionLocal
from database.models import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register_user(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    password_hash = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=password_hash
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id
    }


@router.post("/login")
def login_user(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if user.is_locked:
        raise HTTPException(
            status_code=403,
            detail="Your account is locked. Please reset your password."
        )

    password_correct = bcrypt.checkpw(
        data.password.encode("utf-8"),
        user.password_hash.encode("utf-8")
    )

    if not password_correct:

        user.failed_attempts += 1

        if user.failed_attempts >= 5:
            user.is_locked = True
            db.commit()

            raise HTTPException(
                status_code=403,
                detail="Account locked after 5 failed attempts."
            )

        db.commit()

        raise HTTPException(
            status_code=401,
            detail=f"Invalid password. Remaining attempts: {5-user.failed_attempts}"
        )

    user.failed_attempts = 0
    user.is_locked = False
    db.commit()

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    password_hash = bcrypt.hashpw(
        data.new_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user.password_hash = password_hash
    user.failed_attempts = 0
    user.is_locked = False

    db.commit()

    return {
        "message": "Password reset successful"
    }
