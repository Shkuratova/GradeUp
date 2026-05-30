from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    computed_field,
)

from db.models import ConfirmationTypes
from schemas.profiles import ProfileList
from schemas.users import UserSchema, UserInfo
from utils.roles import UserRole


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


class UserProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user: UserSchema
    profile: ProfileList

class UserProgressList(UserInfo):
    profile_id: int | None = None
    title: str | None = None
    level_name: str | None = None
    level_cnt: int | None = Field(None, exclude=True)
    closed_levels_cnt: int | None = Field(None, exclude=True)
    skill_cnt: int | None = Field(None, exclude=True)
    accepted_cnt: int | None = Field(None, exclude=True)

    @computed_field
    @property
    def progress(self) -> float | None:
        return self.closed_levels_cnt / self.level_cnt * 100 if self.level_cnt else 0

    @computed_field
    @property
    def current_level_progress(self) -> float:
        return self.accepted_cnt / self.skill_cnt if self.skill_cnt else 0

    @computed_field
    @property
    def ready_gradeup(self) -> bool:
        if self.skill_cnt and self.skill_cnt == self.accepted_cnt:
           return True
        return False


class Stage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    confirmation_type: ConfirmationTypes


class Skill(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    stages: list[Stage]


class CurrentLevel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    num: int
    level_name: str
    skills: list[Skill]


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
