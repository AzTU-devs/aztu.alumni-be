from app.core.database import Base
from sqlalchemy import Column, Integer, Text, TIMESTAMP, func

class VacancyRequirement(Base):
    __tablename__ = "vacancy_requirements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vacancy_code = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now())