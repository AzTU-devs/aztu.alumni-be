from fastapi import FastAPI
from app.core.database import get_db

app = FastAPI(title="AZTU Alumni API")

@app.get("/")
async def root():
    return {"message": "AZTU Alumni API is running!"}

@app.get("/health")
async def health_check(db = get_db()):
    return {"status": "ok"}