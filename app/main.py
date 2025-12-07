import os
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from fastapi_limiter import FastAPILimiter
from fastapi.staticfiles import StaticFiles
from app.core.redis_client import get_redis
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.alumni import router as alumni_router
from app.api.v1.routes.vacancy import router as vacancy_router
from app.api.v1.routes.education import router as education_router
from app.api.v1.routes.user_photos import router as user_photo_router
from app.api.v1.routes.work_experience import router as experience_router
from app.api.v1.routes.vacancy_category import router as vacancy_category_router
from app.api.v1.routes.vacancy_requirements import router as vacancy_requirement_router

from app.core.database import get_db, engine

app = FastAPI(title="AZTU Alumni API")

bearer_scheme = HTTPBearer()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mezun.aztu.edu.az", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(alumni_router, prefix="/api/alumni", tags=["Alumni"])
app.include_router(vacancy_router, prefix="/api/vacancy", tags=["Vacancy"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(education_router, prefix="/api/education", tags=["Education"])
app.include_router(experience_router, prefix="/api/experience", tags=["Experience"])
app.include_router(user_photo_router, prefix="/api/profile-photo", tags=["User profile photo"])
app.include_router(vacancy_category_router, prefix="/api/vacancy/category", tags=["Vacancy Category"])
app.include_router(vacancy_requirement_router, prefix="/api/vacancy/requirement", tags=["Vacancy Requirements"])

# Swagger Security
app.openapi_schema = app.openapi()
if app.openapi_schema:
    if "components" not in app.openapi_schema:
        app.openapi_schema["components"] = {}
    app.openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in app.openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

@app.on_event("startup")
async def on_startup():
    await engine.dispose()
    redis_client = await get_redis()
    await FastAPILimiter.init(redis_client)

@app.get("/")
async def root():
    return {"message": "AZTU Alumni API is running!"}

@app.get("/health")
async def health_check(db = get_db()):
    return {"status": "ok"}