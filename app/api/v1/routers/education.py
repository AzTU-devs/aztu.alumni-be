from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.api.v1.schemas.education import EducationCreate, EducationUpdate, EducationOut
from app.services import education as service

router = APIRouter(prefix="/education", tags=["Education"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[EducationOut])
def get_all(db: Session = Depends(get_db)):
    return service.get_all(db)


@router.get("/{education_id}", response_model=EducationOut)
def get_one(education_id: int, db: Session = Depends(get_db)):
    item = service.get_by_id(db, education_id)
    if not item:
        raise HTTPException(404, "Education not found")
    return item


@router.post("/", response_model=EducationOut)
def create_item(data: EducationCreate, db: Session = Depends(get_db)):
    return service.create(db, data)


@router.put("/{education_id}", response_model=EducationOut)
def update_item(education_id: int, data: EducationUpdate, db: Session = Depends(get_db)):
    updated = service.update(db, education_id, data)
    if not updated:
        raise HTTPException(404, "Education not found")
    return updated


@router.delete("/{education_id}")
def delete_item(education_id: int, db: Session = Depends(get_db)):
    deleted = service.delete(db, education_id)
    if not deleted:
        raise HTTPException(404, "Education not found")
    return {"message": "Deleted successfully"}
