from sqlalchemy import (
    Date,
    Column,
    Integer,
    String
)
from datetime import datetime
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID

class UserPhotos(Base):
    __tablename__ = "user_photos"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    image = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, onupdate=datetime.utcnow())