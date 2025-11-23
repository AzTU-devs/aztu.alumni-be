from datetime import date, datetime
from enum import Enum, IntEnum
from typing import Optional

from pydantic import BaseModel

class VacancyCategoryCreate(BaseModel):
    title: str