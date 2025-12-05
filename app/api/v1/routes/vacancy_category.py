from app.core.database import get_db
from fastapi import APIRouter, Depends
from app.services.vacancy_category import *
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.vancacy_category import *

router = APIRouter()

@router.get("/all")
async def get_categories_endpoint(
    db: AsyncSession = Depends(get_db)
):
    return await get_categories(
        db=db
    )

@router.post("/create")
async def create_category_endpoint(
    cat_request: VacancyCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_category(
        cat_request=cat_request,
        db=db
    )

@router.put("/update")
async def update_vacancy_category_endpoint(
    requst: UpdateVacancyCategory,
    db: AsyncSession = Depends(get_db)
):
    return await update_category(
        request=requst,
        db=db
    )

@router.delete("/{category_code}/delete")
async def delete_category_endpoint(
    category_code: str,
    db: AsyncSession = Depends(get_db)
):
    return await delete_category(
        category_code=category_code,
        db=db
    )