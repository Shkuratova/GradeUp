from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
    computed_field,
)


class ProfileBase(BaseModel):
    id: int
    title: str
    department_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class ProfileFilter(BaseModel):
    id: int | None = None
    department_id: int | None = None


class ProfileAdd(BaseModel):
    title: str
    description: str | None = None
    department_id: int | None = None


class LevelBase(BaseModel):
    id: int
    num: int
    level_name: str
    model_config = ConfigDict(from_attributes=True)


class LevelAdd(BaseModel):
    profile_id: int
    num: int = Field(..., gt=0)
    level_name: str


class LevelSkillAdd(BaseModel):
    skill_id: int
    profile_level_id: int = Field(default=1)


class ProfileList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str


class SLevelAdd(BaseModel):
    level_name: str
    num: int = Field(..., gt=0)
    skills: list[int] = []


class SLevelUpdate(SLevelAdd):
    id: int | None = None


class SProfileAdd(BaseModel):
    profile: ProfileAdd
    levels: list[SLevelAdd] | None = None

    @model_validator(mode="after")
    def check_level(self):
        if not self.levels:
            return self

        level_nums = [lvl.num for lvl in self.levels]
        expected_nums = list(range(1, len(level_nums) + 1))

        if sorted(level_nums) != expected_nums:
            raise ValueError(
                f"Номера уровней должны быть уникальными и идти последовательно от 1 до {len(level_nums)}. "
            )

        all_skills = []
        for lvl in self.levels:
            for skill in lvl.skills:
                if skill in all_skills:
                    raise ValueError(
                        f"Навык с id = {skill} встречается в нескольких уровнях."
                    )
            all_skills.extend(lvl.skills)
        return self


class SProfileUpdate(SProfileAdd):
    levels: list[SLevelUpdate] | None = None


class SkillList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str


class SLevelSkill(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill: SkillList


class LevelSkill(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill: SkillList


class LevelVersion(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    version: int
    skills: list[LevelSkill] | None = Field(default=None, exclude=True)

    @computed_field
    @property
    def skill_list(self) -> list[SkillList]:
        if self.skills:
            return [ls.skill for ls in self.skills if ls.skill]
        return []


class LevelDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    num: int
    level_name: str
    versions: list[LevelVersion] | None = Field(None, exclude=True)

    @computed_field
    @property
    def last_version(self) -> int | None:
        if self.versions is None:
            return None
        return self.versions[0].version

    @computed_field
    @property
    def skills(self) -> list[SkillList] | None:
        return self.versions[0].skill_list


class ProfileDetail(ProfileBase):
    description: str | None = None
    levels: list[LevelDetail]

