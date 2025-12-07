from sqlalchemy import (
    DateTime,
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
    locked_until = Column(DateTime)
    last_login = Column(DateTime)
    role = Column(Integer)
    # 1 - user
    # 2 - admin
    # 3 - dev
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow())