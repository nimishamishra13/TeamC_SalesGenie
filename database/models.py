from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from database.connection import Base
from datetime import datetime


# ==========================
# MODULE 1 : LEADS
# ==========================

class Lead(Base):

    __tablename__ = "leads"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        nullable=False
    )

    company = Column(
        String
    )

    status = Column(
        String
    )

    notes = Column(
        String
    )


    __table_args__ = (
        UniqueConstraint(
            "email",
            name="uq_email"
        ),
    )



# ==========================
# MODULE 5 : CONVERSATIONS
# ==========================

class Conversation(Base):

    __tablename__ = "conversations"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    lead_id = Column(
        Integer
    )


    conversation_type = Column(
        String
    )


    transcript = Column(
        Text
    )


    summary = Column(
        Text
    )


    key_points = Column(
        Text
    )


    action_items = Column(
        Text
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )



# ==========================
# MODULE 5 : CRM ACTIVITY
# ==========================

class CRMActivity(Base):

    __tablename__ = "crm_activity"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    lead_id = Column(
        Integer
    )


    activity_type = Column(
        String
    )


    description = Column(
        Text
    )


    status = Column(
        String
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    # ==========================
# MODULE 6 : OUTREACH HISTORY
# ==========================

class OutreachHistory(Base):

    __tablename__ = "outreach_history"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    lead_id = Column(
        Integer
    )


    company = Column(
        String
    )


    industry = Column(
        String
    )


    message = Column(
        Text
    )


    tone = Column(
        String
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )



# ==========================
# MODULE 6 : LEAD SCORES
# ==========================

class LeadScore(Base):

    __tablename__ = "lead_scores"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    lead_id = Column(
        Integer
    )


    company = Column(
        String
    )


    industry = Column(
        String
    )


    score = Column(
        Integer
    )


    recommendation = Column(
        Text
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
