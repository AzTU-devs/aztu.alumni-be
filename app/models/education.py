from sqlalchemy import (
    Date,
    Column,
    Integer,
    String,
    DateTime
)
from datetime import datetime
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), nullable=False)
    university = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    major = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    # ?
    gpa = Column(Integer)
    # ?
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)