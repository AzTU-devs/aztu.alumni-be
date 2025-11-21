from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field
from fastapi import UploadFile, File

class UserPhotosBase(BaseModel):
    uuid: str
    image: str

class UploadPhoto(BaseModel):
    uuid: str