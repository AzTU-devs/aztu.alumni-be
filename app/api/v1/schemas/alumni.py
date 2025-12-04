from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional


# Shared fields (for reading)
class AlumniBase(BaseModel):
    uuid: str
    name: str
    surname: str
    father_name: str
    gender: str = Field(..., max_length=10)

# For creating a new alumni
class AlumniCreate(AlumniBase):
    pass


# For updating existing alumni
class AlumniUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    father_name: Optional[str] = None
    gender: Optional[str] = Field(None, max_length=10)
    birth_date: Optional[date] = None
    phone_number: Optional[str] = None
    phone_is_public: Optional[bool] = None
    registered_city: Optional[str] = None
    registered_address: Optional[str] = None
    address: Optional[str] = None
    address_is_public: Optional[bool] = None
    military_obligation: Optional[int] = None
    married: Optional[bool] = None

class CompleteProfile(BaseModel):
    uuid: str
    name: str
    surname: str
    father_name: str
    birth_date: str
    phone_number: str
    phone_is_public: bool
    fin_code: str
    job_title: str
    registered_city: str
    registered_address: str
    address: str
    address_is_public: bool
    military_obligation: int
    married: bool

# For returning alumni data to the frontend
class AlumniResponse(AlumniBase):
    id: int
    created_at: date
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # For ORM compatibility