from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    DateTime,
    Text
)
from datetime import datetime
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID, INET


class AuthUserDevice(Base):
    __tablename__ = "auth_user_devices"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    user_uuid = Column(UUID(as_uuid=True), nullable=False)
    device_id = Column(UUID(as_uuid=True), nullable=False)
    user_agent = Column(Text)
    device_name = Column(Text)
    browser = Column(Text)
    os = Column(Text)
    ip = Column(INET)
    location = Column(Text)
    is_mobile = Column(Boolean)
    first_used_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_blacklisted = Column(Boolean, nullable=False, default=False)
    blacklisted_reason = Column(Text)
    blacklisted_at = Column(DateTime)