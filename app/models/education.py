import uuid
from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, Float, Numeric
from sqlalchemy.sql import func
from app.core.db import Base

class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, default=lambda: str(uuid.uuid4()), nullable=False, unique=True)
    university = Column(String, nullable=False)
    degree = Column(Integer, nullable=False)   # 1 bachelor, 2 master, 3 phd
    major = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    gpa = Column(Numeric(3, 2), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())