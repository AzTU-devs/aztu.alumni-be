from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.v1.schemas.education import EducationCreate, EducationUpdate
from app.services import education as service

router = APIRouter(prefix="/api/education", tags=["Education"])


@router.get("/")
async def get_all(db: AsyncSession = Depends(get_db)):
    return await service.get_all(db)


@router.get("/{uuid}")
async def get_one(uuid: str, db: AsyncSession = Depends(get_db)):
    return await service.get_by_uuid_response(db, uuid)


@router.post("/")
async def create_item(data: EducationCreate, db: AsyncSession = Depends(get_db)):
    return await service.create(db, data)


@router.put("/{uuid}")
async def update_item(uuid: str, data: EducationUpdate, db: AsyncSession = Depends(get_db)):
    return await service.update(db, uuid, data)


@router.delete("/{uuid}")
async def delete_item(uuid: str, db: AsyncSession = Depends(get_db)):
    return await service.delete(db, uuid)
