
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, text, ForeignKey
from database import Base
from sqlalchemy import Date
from sqlalchemy.dialects.postgresql import JSONB


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
    

class CV(Base):
    __tablename__ = "cvs"

    cv_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    file_name = Column(
        String,
        nullable=False
    )

    file_path = Column(
        Text,
        nullable=False
    )

    extracted_text = Column(
        Text,
        nullable=True
    )

    uploaded_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
class Opportunity(Base):
    __tablename__ = "opportunities"

    opportunity_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    company = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    location = Column(
        String(150),
        nullable=True
    )

    employment_type = Column(
        String(50),
        nullable=True
    )

    application_url = Column(
        Text,
        nullable=True
    )

    requirements = Column(
    JSONB,
    nullable=True,
    server_default=text("'[]'::jsonb")
)

    deadline = Column(
        Date,
        nullable=True
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )