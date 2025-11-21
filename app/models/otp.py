from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID

class Otp(Base):
    __tablename__ = "otp"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    otp_code = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime)