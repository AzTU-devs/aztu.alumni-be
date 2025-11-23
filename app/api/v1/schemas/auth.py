from datetime import date
from pydantic import BaseModel, EmailStr

class Signup(BaseModel):
    name: str
    surname: str
    father_name: str
    gender: str
    birth_date: date
    major_code: str
    email: EmailStr
    password: str
    education_degree: str
    start_date: date
    end_date: date

class VerifySignup(BaseModel):
    name: str
    surname: str
    father_name: str
    gender: str
    birth_date: date
    major_code: str
    email: EmailStr
    password: str
    education_degree: str
    start_date: date
    end_date: date
    otp: int

class Signin(BaseModel):
    email: str
    password: str