from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_name: str

class CategoryAdd(BaseModel):
    category_name: str

class SkillCategory(BaseModel):
    skill_id: int
    category_id: int