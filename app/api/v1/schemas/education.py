from datetime import date
from typing import Optional
from pydantic import BaseModel

class EducationBase(BaseModel):
    uuid: str
    university: str
    start_date: date
    end_date: Optional[date]
    degree: str
    major: str
    gpa: int

class CreateEducation(EducationBase):
    pass