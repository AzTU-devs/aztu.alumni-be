from sqlalchemy.orm import Session
from app.models.language import Language
from app.api.v1.schemas.language import (
    LanguageCreate, LanguageUpdate
)

def get_all(db: Session):
    return db.query(Language).all()


def get_by_id(db: Session, lang_id: int):
    return db.query(Language).filter(Language.id == lang_id).first()


def create(db: Session, data: LanguageCreate):
    new_item = Language(**data.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def update(db: Session, lang_id: int, data: LanguageUpdate):
    item = get_by_id(db, lang_id)
    if not item:
        return None

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, lang_id: int):
    item = get_by_id(db, lang_id)
    if not item:
        return False

    db.delete(item)
    db.commit()
    return True
