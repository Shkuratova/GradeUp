from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    computed_field,
    EmailStr,
)

from db.models import ConfirmationTypes
from schemas.profiles import ProfileList
from schemas.users import SUser, UserFIO


class UserProfileFilter(BaseModel):
    profile_id: int  | None = None
    user_id: int | None = None
    departments_id: list[int] | None = None
    role_id: int | None = None

class UserProfileBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    profile_id: int
    current_level_id: int


class UserProfileAdd(BaseModel):
    user_id: int
    profile_id: int


class UserProfileTitle(UserProfileBase):
    profile: ProfileList = Field(exclude=True)

    @computed_field
    def title(self) -> str:
        return self.profile.title


class UserProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user: UserFIO
    profile: ProfileList


class UserProfileProgressList(BaseModel):
    user_id: int
    profile_id: int | None = None
    first_name: str
    last_name: str
    patronymic: str
    email: EmailStr
    position: str | None = None
    profile_title: str | None = None
    department_id: int | None = None
    department_name: str | None = None
    role_id: int
    role_name: str
    total_cnt: int | None = None
    completed_cnt: int | None = None

    @computed_field
    @property
    def progress(self) -> float | None:
        if self.total_cnt:
            return self.completed_cnt / self.total_cnt * 100 if self.total_cnt else 0


class Stage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    confirmation_type: ConfirmationTypes


class Skill(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    stages: list[Stage]


class LevelSkill(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill: Skill = Field(exclude=True)

    @computed_field
    def skill_id(self) -> int:
        return self.skill.id

    @computed_field
    def title(self) -> str:
        return self.skill.title

    @computed_field
    def stages(self) -> list[Stage]:
        return self.skill.stages


class CurrentLevel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    num: int
    level_name: str
    skills: list[LevelSkill]


class ProfileAvailableSkills(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    profile_id: int
    user_id: int
    current_level: CurrentLevel

class UserStageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_accepted: bool
    stage_version_id: int

class UserStageAdd(BaseModel):
    user_id: int
    stage_id: int
    is_accepted: bool = False
    comment: str | None = None

class UserStageProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    stage_id: int
    confirmation_type: ConfirmationTypes
    stage_accepted: bool | None = None

class UserSkillProgress(BaseModel):
    skill_id: int
    title: str
    stages: list[UserStageProgress | None]

    @computed_field
    @property
    def skill_pcnt(self) -> int:
        if not self.stages:
            return 0

        accepted = sum(1 for stage in self.stages if stage.stage_accepted is True)

        return round(accepted / len(self.stages) * 100)


class UserLevelProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    profile_level_id: int
    user_level_id: int | None = None
    num: int
    level_name: str
    is_closed: bool | None = None
    skills: list[UserSkillProgress | None]

    @computed_field
    @property
    def level_pcnt(self) -> int:
        if not self.skills:
            return 0

        completed = sum(1 for skill in self.skills if skill.skill_pcnt == 100)

        return round(completed / len(self.skills) * 100)


class UserProfileProgress(UserProfileBase):
    title: str
    profile_levels: list[UserLevelProgress]


class Level(BaseModel):
    id: int
    num: int
    level_name: str

class GradeUpResult(BaseModel):
    profile_id: int
    old_level: Level
    new_level: Level
