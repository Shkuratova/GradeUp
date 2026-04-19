from pydantic import BaseModel, Field, ConfigDict, field_validator


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

class SLevelAdd(BaseModel):
    level: str
    skills: list[int]  = []

class SProfileAdd(BaseModel):
    profile: ProfileAdd
    levels: list[SLevelAdd] | None = None


class SSkill(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str

class SLevel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    level: str
    skills: list[SSkill]

    @field_validator("skills", mode="before")
    @classmethod
    def extract_skills(cls, values):
        return [v.skill for v in values if v.skill]


class SProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None = None
    levels: list[SLevel]
