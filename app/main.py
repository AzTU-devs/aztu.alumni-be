from fastapi import FastAPI
from app.api.v1.routers.education import router as education_router
from app.core.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(education_router)
