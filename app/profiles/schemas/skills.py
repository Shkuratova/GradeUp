from pydantic import BaseModel, ConfigDict, Field, computed_field
from app.auth import SUserFullInfo
from datetime import datetime

class SSkillBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str

class SSkill(SSkillBase):
    id: int 
    creator_id: int


class SSkillInfo(SSkillBase):
    num_stages: int 
    creator: str 
    created_at: datetime

    

class SCertification(BaseModel):
    model_config = ConfigDict(from_attributes=True)