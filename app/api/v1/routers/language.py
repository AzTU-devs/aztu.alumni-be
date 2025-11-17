from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.api.v1.schemas.language import (
    LanguageCreate, LanguageUpdate, LanguageOut
)
from app.services import language 

router = APIRouter(prefix="/languages", tags=["Languages"])


@router.get("/", response_model=list[LanguageOut])
def list_languages(db: Session = Depends(get_db)):
    return language.get_all(db)


@router.get("/{lang_id}", response_model=LanguageOut)
def get_language(lang_id: int, db: Session = Depends(get_db)):
    item = language.get_by_id(db, lang_id)
    if not item:
        raise HTTPException(404, "Language not found")
    return item


@router.post("/", response_model=LanguageOut)
def create_language(data: LanguageCreate, db: Session = Depends(get_db)):
    return language.create(db, data)


@router.put("/{lang_id}", response_model=LanguageOut)
def update_language(lang_id: int, data: LanguageUpdate, db: Session = Depends(get_db)):
    updated = language.update(db, lang_id, data)
    if not updated:
        raise HTTPException(404, "Language not found")
    return updated


@router.delete("/{lang_id}")
def delete_language(lang_id: int, db: Session = Depends(get_db)):
    deleted = language.delete(db, lang_id)
    if not deleted:
        raise HTTPException(404, "Language not found")
    return {"message": "Deleted successfully"}
