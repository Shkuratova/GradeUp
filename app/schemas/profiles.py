from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


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
    num: int
    level_name: str
    model_config = ConfigDict(from_attributes=True)

class ProfileLevels(SProfile):
    levels: list[LevelBase]

class LevelAdd(BaseModel):
    profile_id: int
    num: int = Field(..., gt=0)
    level_name: str


class LevelSkill(BaseModel):
    id: int
    skill_id: int
    profile_level_id: int
    model_config = ConfigDict(from_attributes=True)

class LevelSkillAdd(BaseModel):
    skill_id: int
    profile_level_id: int = Field(default=1)


class ProfileList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None = None


class SLevelAdd(BaseModel):
    level_name: str
    num: int = Field(..., gt=0)
    skills: list[int]  = []

class SLevelUpdate(SLevelAdd):
    id: int | None = None

class SProfileAdd(BaseModel):
    profile: ProfileAdd
    levels: list[SLevelAdd] | None = None

    @model_validator(mode="after")
    def check_skills(self):
        if not self.levels:
            return self
        all_skills = []
        for lvl in self.levels:
            for skill in lvl.skills:
                if skill in all_skills:
                    raise ValueError(
                        f"Навык с id = {skill} встречается в нескольких уровнях."
                    )
                all_skills += lvl.skills
        return self

class SProfileUpdate(SProfileAdd):
    levels: list[SLevelUpdate] | None = None

class SSkill(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str

class SLevelSkill(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill: SSkill

class SLevel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    num: int
    level_name: str
    last_version: int | None = None
    skills: list[SSkill]

class SProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None = None
    levels: list[SLevel]
