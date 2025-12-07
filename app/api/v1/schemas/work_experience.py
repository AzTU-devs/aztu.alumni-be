from datetime import date
from typing import Optional
from pydantic import BaseModel

class CreateExperience(BaseModel):
    uuid: str
    company: str
    job_title: str
    start_date: date
    end_date: Optional[date] = None
    employment_type: int
    job_location_type: int
    description: Optional[str] = None