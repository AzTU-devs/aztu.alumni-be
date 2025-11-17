from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

ALLOWED_LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}

class LanguageBase(BaseModel):
    language: str
    level: str

    @field_validator("level")
    def validate_level(cls, value):
        if value not in ALLOWED_LEVELS:
            raise ValueError("level must be one of A1, A2, B1, B2, C1, C2")
        return value


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    language: Optional[str] = None
    level: Optional[str] = None

    @field_validator("level")
    def validate_level(cls, value):
        if value is not None and value not in ALLOWED_LEVELS:
            raise ValueError("level must be one of A1, A2, B1, B2, C1, C2")
        return value


class LanguageOut(LanguageBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
