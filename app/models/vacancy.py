import enum
from app.core.database import Base
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, Date, Text, Enum, DateTime

class JobLocationType(enum.IntEnum):
    on_site = 1
    hybrid = 2
    remote = 3


class EmploymentType(enum.IntEnum):
    full_time = 1
    part_time = 2
    self_employed = 3
    freelance = 4
    contract = 5
    internship = 6
    volunteering = 7


class VacancyStatus(enum.IntEnum):
    active = 1
    closed = 2
    expired = 3
    draft = 4


class Currency(enum.Enum):
    AZN = "AZN"
    EUR = "EUR"
    USD = "USD"


class Vacancy(Base):
    __tablename__ = "vacancy"

    id = Column(Integer, primary_key=True, index=True)
    vacancy_code = Column(String, nullable=False, unique=True)
    category_code = Column(String, nullable=True)
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    working_hours = Column(String, nullable=False)
    job_location_type = Column(Enum(JobLocationType, name="job_location_type", native_enum=True), nullable=False)
    employment_type = Column(Enum(EmploymentType, name="employment_type", native_enum=True), nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    currency = Column(Enum(Currency, name="currency_type", native_enum=True), nullable=False)
    is_salary_public = Column(Boolean, nullable=False, default=True)
    deadline = Column(Date, nullable=False)
    status = Column(Enum(VacancyStatus, name="vacancy_status", native_enum=True), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)