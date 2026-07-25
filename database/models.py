from sqlalchemy import Column, Integer, String, UniqueConstraint
from database.connection import Base   # ✅ FIXED

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String)
    status = Column(String)
    notes = Column(String)

    # Prevent duplicate emails
    __table_args__ = (
        UniqueConstraint("email", name="uq_email"),
    )