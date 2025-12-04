import random
from datetime import datetime
from sqlalchemy import select
from app.core.session import get_db
from fastapi import Depends, status
from app.api.v1.schemas.vacancy import *
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.vancacy_category import *
from app.models.vacancy_category import VacancyCategory

def generate_category_code():
    random_number = random.randint(100000, 999999)
    return f"{random_number}"

async def create_category(
    cat_request: VacancyCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        category_query = await db.execute(
            select(VacancyCategory)
            .where(VacancyCategory.title == cat_request.title)
        )

        title_exists = category_query.scalar_one_or_none()

        if title_exists:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "Title already exists"
                }, status_code=status.HTTP_409_CONFLICT
            )

        category_code = generate_category_code()

        new_category = VacancyCategory(
            category_code=category_code,
            title=cat_request.title,
            created_at=datetime.utcnow()
        )

        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Category created successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }
        )

async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    try:
        category_query = await db.execute(
            select(VacancyCategory)
        )

        categories = category_query.scalars().all()

        if not categories:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "No content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        category_arr = []

        for category in categories:
            cat_obj = {
                "category_code": category.category_code,
                "title": category.title,
                "created_at": category.created_at.isoformat() if category.created_at else None
            }

            category_arr.append(cat_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Categories fetched successfully.",
                "categories": category_arr
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }
        )

async def update_category(
    request: UpdateVacancyCategory,
    db: AsyncSession = Depends(get_db)
):
    try:
        category_query = await db.execute(
            select(VacancyCategory)
            .where(VacancyCategory.category_code == request.category_code)
        )

        category = category_query.scalar_one_or_none()

        if not category:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Category not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        category.title = request.title

        await db.commit()
        await db.refresh(category)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Category updateed successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }
        )