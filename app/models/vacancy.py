import enum
from datetime import datetime
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime

class Vacancy(Base):
    __tablename__ = "vacancy"

    id = Column(Integer, primary_key=True, index=True)
    vacancy_code = Column(String, nullable=False, unique=True)
    category_code = Column(String, nullable=True)
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    working_hours = Column(String, nullable=False)
    job_location_type = Column(Integer, nullable=False)
    employment_type = Column(Integer, nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    currency = Column(Integer, nullable=False)
    is_salary_public = Column(Boolean, nullable=False, default=True)
    deadline = Column(Date, nullable=False)
    status = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)