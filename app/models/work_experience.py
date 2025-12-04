import uuid
from datetime import datetime
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, Text, Date, TIMESTAMP

class WorkExperience(Base):
    __tablename__ = "work_experience"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    company = Column(Text, nullable=False)
    job_title = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    employment_type = Column(Integer, nullable=False)
    # 1 - full-time
    # 2 - part-time
    # 3 - self-employed
    # 4 - freelance
    # 5 - contract
    # 6 - internship
    # 7 - volunteering
    job_location_type = Column(Integer, nullable=False)
    # 1 - on-site
    # 2 - hybrid
    # 3 - remote
    description = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, onupdate=datetime.utcnow)