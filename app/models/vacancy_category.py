from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base


class VacancyCategory(Base):
    __tablename__ = "vacancy_category"

    id = Column(Integer, primary_key=True, index=True)
    category_code = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)