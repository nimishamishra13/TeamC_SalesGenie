from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

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
    conversations = relationship("Conversation", back_populates="lead")


from sqlalchemy import ForeignKey, Text

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(Integer, ForeignKey("leads.id"))

    transcript = Column(Text)

    summary = Column(Text)

    sentiment = Column(String)

    buying_intent = Column(String)

    next_action = Column(Text)

    crm_notes = Column(Text)

    lead = relationship("Lead", back_populates="conversations")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True, nullable=False)

    password_hash = Column(String, nullable=False)
