from sqlalchemy import Column, Integer, String
from database.connection import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    company = Column(String)

    contact = Column(String)

    designation = Column(String)

    email = Column(String)

    phone = Column(String)

    website = Column(String)

    location = Column(String)

    industry = Column(String)

    score = Column(Integer)

    status = Column(String)

    notes = Column(String)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True, nullable=False)

    password_hash = Column(String, nullable=False)
