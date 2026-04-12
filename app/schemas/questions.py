from pydantic import BaseModel, Field, ConfigDict

class QuestionBase(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SQuestion(QuestionBase):
    num: int
    question: str
    answer: str


class QuestionAdd(BaseModel):
    num: int = Field(..., gt=0)
    stage_id: int
    question: str
    answer: str


class QuestionUpdate(BaseModel):
    id: int | None = Field(default=None, exclude=True)
    num: int
    stage_id: int
    question: str
    answer: str

class QuestionFilter(BaseModel):
    stage_id: int
    num: int  | None = None
