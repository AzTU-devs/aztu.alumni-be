from fastapi import FastAPI
from app.core.database import get_db
from app.core.database import engine
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.alumni import router as alumni_router
from app.api.v1.routes.user_photos import router as user_photo_router

app = FastAPI(title="AZTU Alumni API")

@app.on_event("startup")
async def on_startup():
    await engine.dispose()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mezun.aztu.edu.az", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(alumni_router, prefix="/api/alumni", tags=["Alumni"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_photo_router, prefix="/api/profile-photo", tags=["User profile photo"])

@app.get("/")
async def root():
    return {"message": "AZTU Alumni API is running!"}

@app.get("/health")
async def health_check(db = get_db()):
    return {"status": "ok"}