import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
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
    ai_status = Column(String)
    deal_value = Column(Float, default=0)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    closed_at = Column(
        DateTime,
        nullable=True
    )
    conversations = relationship(
        "Conversation",
        back_populates="lead"
    )

    crm_activities = relationship(
        "CRMActivity",
        back_populates="lead",
        cascade="all, delete-orphan"
    )

    outreach_history = relationship(
        "OutreachHistory",
        back_populates="lead",
        cascade="all, delete-orphan"
    )


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
    failed_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)

class CRMActivity(Base):
    __tablename__ = "crm_activities"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=False
    )

    activity_type = Column(
        String,
        nullable=False
    )

    description = Column(Text)

    activity_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    lead = relationship(
        "Lead",
        back_populates="crm_activities"
    )

class OutreachHistory(Base):
    __tablename__ = "outreach_history"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=False
    )

    channel = Column(String)

    subject = Column(String)

    content = Column(Text)

    status = Column(
        String,
        default="Generated"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    lead = relationship(
        "Lead",
        back_populates="outreach_history"
    )
