from datetime import date, datetime
from enum import Enum, IntEnum
from typing import Optional

from pydantic import BaseModel


# Enum replicas for Pydantic
class JobLocationTypeEnum(IntEnum):
    on_site = 1
    hybrid = 2
    remote = 3


class EmploymentTypeEnum(IntEnum):
    full_time = 1
    part_time = 2
    self_employed = 3
    freelance = 4
    contract = 5
    internship = 6
    volunteering = 7


class VacancyStatusEnum(IntEnum):
    active = 1
    closed = 2
    expired = 3
    draft = 4


class CurrencyEnum(str, Enum):
    AZN = "AZN"
    EUR = "EUR"
    USD = "USD"


# Base schema shared by Create and Update
class VacancyBase(BaseModel):
    category_code: Optional[str]
    job_title: str
    company: str
    working_hours: str
    job_location_type: JobLocationTypeEnum
    employment_type: EmploymentTypeEnum
    country: str
    city: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: CurrencyEnum
    is_salary_public: bool = True
    deadline: date
    status: VacancyStatusEnum


# Schema for creating a new vacancy
class VacancyCreate(VacancyBase):
    pass


# Schema for updating an existing vacancy (all fields optional)
class VacancyUpdate(BaseModel):
    category_code: Optional[str]
    job_title: Optional[str]
    company: Optional[str]
    working_hours: Optional[str]
    job_location_type: Optional[JobLocationTypeEnum]
    employment_type: Optional[EmploymentTypeEnum]
    country: Optional[str]
    city: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    currency: Optional[CurrencyEnum]
    is_salary_public: Optional[bool]
    deadline: Optional[date]
    status: Optional[VacancyStatusEnum]


# Schema returned in responses (includes DB fields)
class VacancyResponse(VacancyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True