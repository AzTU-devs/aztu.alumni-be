from app.services.alumni import *
from app.core.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.alumni import AlumniCreate

router = APIRouter()


@router.get("/all")
async def get_alumnis_endpoint(
    start: int = Query(...),
    end: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    return await get_alumnis(
        start=start,
        end=end,
        db=db
    )

@router.get("/{uuid}/details")
async def get_alumnis_endpoint(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    return await get_alumnis(
        uuid=uuid,
        db=db
    )

@router.post("/create")
async def create_alumni_endpoint(
    request: AlumniCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_alumni(
        request=request,
        db=db
    )

@router.delete("/{uuid}/delete")
async def delete_alumni_endpoint(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    return await delete_alumni(
        uuid=uuid,
        db=db
    )