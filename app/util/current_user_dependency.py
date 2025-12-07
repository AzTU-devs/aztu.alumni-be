from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.util.jwt import decode_auth_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        user = decode_auth_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"uuid": user["uuid"], "role": user["role"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")