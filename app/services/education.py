from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import JSONResponse
from fastapi import status

from app.models.education import Education
from app.api.v1.schemas.education import EducationCreate, EducationUpdate


async def get_by_uuid(db: AsyncSession, uuid: str):
    try:
        result = await db.execute(select(Education).where(Education.uuid == uuid))
        return result.scalar_one_or_none()
    except Exception:
        return None


async def get_all(db: AsyncSession):
    try:
        result = await db.execute(select(Education))
        items = result.scalars().all()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "data": items}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": str(e)}
        )


async def create(db: AsyncSession, data: EducationCreate):
    try:
        new_item = Education(**data.model_dump())
        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"success": True, "data": new_item}
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": str(e)}
        )


async def update(db: AsyncSession, uuid: str, data: EducationUpdate):
    try:
        item = await get_by_uuid(db, uuid)
        if not item:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "Education with this UUID not found"}
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)

        await db.commit()
        await db.refresh(item)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "data": item}
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": str(e)}
        )


async def delete(db: AsyncSession, uuid: str):
    try:
        item = await get_by_uuid(db, uuid)
        if not item:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "Education with this UUID not found"}
            )

        await db.delete(item)
        await db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "message": "Education deleted successfully"}
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": str(e)}
        )
