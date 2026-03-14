from pydantic import BaseModel, Field, ConfigDict

class ProfileBase(BaseModel):
    id: int
    position: str
    model_config = ConfigDict(from_attributes=True)

class ProfileAdd(BaseModel):
    position: str

class LevelBase(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class LevelAdd(BaseModel):
    name: str

class ProfileLevels(ProfileBase):
    levels: list[LevelBase]
