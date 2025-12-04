from datetime import date, datetime
from enum import Enum, IntEnum
from typing import Optional
from pydantic import BaseModel

class CreateRequiremt(BaseModel):
    vacancy_code: str
    title: str