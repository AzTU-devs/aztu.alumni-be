from datetime import datetime
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, Text, TIMESTAMP

class SavedVacancy(Base):
    __tablename__ = "saved_vacancy"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), nullable=False, index=True)
    vacancy_code = Column(Text, nullable=False, index=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)