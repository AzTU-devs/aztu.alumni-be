from sqlalchemy.orm import Session
from app.models.education import Education
from app.api.v1.schemas.education import EducationCreate, EducationUpdate

def get_all(db: Session):
    return db.query(Education).all()

def get_by_id(db: Session, education_id: int):
    return db.query(Education).filter(Education.id == education_id).first()

def create(db: Session, data: EducationCreate):
    new_item = Education(**data.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def update(db: Session, education_id: int, data: EducationUpdate):
    item = get_by_id(db, education_id)
    if not item:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

def delete(db: Session, education_id: int):
    item = get_by_id(db, education_id)
    if not item:
        return False
    
    db.delete(item)
    db.commit()
    return True
