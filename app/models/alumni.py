from sqlalchemy import (
    Date,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)
from datetime import datetime
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID

class Alumni(Base):
    __tablename__ = "alumni"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    father_name = Column(String, nullable=False)
    gender = Column(String(10), nullable=False)
    birth_date = Column(Date, nullable=False)
    phone_number = Column(String, unique=True)
    phone_is_public = Column(Boolean, default=False)
    fin_code = Column(String(7), unique=True)
    job_title = Column(String(255))
    registered_city = Column(String)
    registered_address = Column(String)
    address = Column(String)
    address_is_public = Column(Boolean, default=False)
    military_obligation = Column(Integer)
    # 1, 2, 3, 4, 5
    # 1 - var (completed)
    # 2 - yoxdur (not done)
    # 3 - herbi xidmete yollaniram
    # 4 - muveqqeti olaraq getmirem
    # 5 - diger (other options)
    married = Column(Boolean)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, onupdate=datetime.utcnow())
    education_degree = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)