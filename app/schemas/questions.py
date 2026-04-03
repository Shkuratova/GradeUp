from pydantic import BaseModel, Field, ConfigDict

class QuestionBase(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SQuestion(QuestionBase):
    question: str
    answer: str


class QuestionAdd(BaseModel):
    num: int
    question: str
    answer: str
    stage_id: int
    creator_id: int

