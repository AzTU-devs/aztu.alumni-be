from app.services.auth import *
from app.core.database import get_db
from app.api.v1.schemas.auth import *
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

router = APIRouter()

@router.post("/signup")
async def signup_endpoint(
    signup_request: Signup,
    db: AsyncSession = Depends(get_db)
):
    return await signup(
        signup_request=signup_request,
        db=db
    )

@router.post("/signup/verify")
async def verify_signup_endpoint(
    request: Request,
    signup_request: VerifySignup,
    db: AsyncSession = Depends(get_db)
):
    return await verify_signup(
        signup_request=signup_request,
        request=request,
        db=db
    )

@router.post("/signin")
async def singin_endpoint(
    signin_request: Signin,
    db: AsyncSession = Depends(get_db)
):
    return await signin(
        signin_request=signin_request,
        db=db
    )