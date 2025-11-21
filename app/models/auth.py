from sqlalchemy import (
    Date,
    Column,
    Integer,
    String,
    Boolean
)
from datetime import datetime
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID


class Auth(Base):
    __tablename__ = "auth"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    failed_attemps = Column(Integer)
    locked_until = Column(Date)
    last_login = Column(Date)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, onupdate=datetime.utcnow())