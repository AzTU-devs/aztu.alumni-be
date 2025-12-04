from pydantic import BaseModel

class VacancyCategoryCreate(BaseModel):
    title: str

class UpdateVacancyCategory(BaseModel):
    category_code: str
    title: str