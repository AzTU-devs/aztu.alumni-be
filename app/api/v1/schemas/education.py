from pydantic import BaseModel
from datetime import datetime
from datetime import date
from typing import Optional

class EducationBase(BaseModel):
    university: str
    degree: int
    major: str
    start_date: date
    end_date: Optional[date] = None
    gpa: Optional[float] = None

class EducationCreate(EducationBase):
    pass

class EducationUpdate(BaseModel):
    university: Optional[str] = None
    degree: Optional[int] = None
    major: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None


class EducationOut(EducationBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

