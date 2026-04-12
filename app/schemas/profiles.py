from pydantic import BaseModel, Field, ConfigDict

class ProfileBase(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)

class SProfile(ProfileBase):
    description: str | None = None

class ProfileAdd(BaseModel):
    title: str
    description: str

class LevelBase(BaseModel):
    id: int
    level: str
    model_config = ConfigDict(from_attributes=True)

class ProfileLevels(SProfile):
    levels: list[LevelBase]

class LevelAdd(BaseModel):
    profile_id: int
    level: str


class LevelSkill(BaseModel):
    id: int
    skill_id: int
    profile_level_id: int
    model_config = ConfigDict(from_attributes=True)

class LevelSkillAdd(BaseModel):
    skill_id: int
    profile_level_id: int = Field(default=1)


class LevelUpdate(BaseModel):
    id: int | None = None
    level: str

class ProfileUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    levels: list[LevelUpdate]

