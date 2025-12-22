from pydantic import BaseModel, EmailStr, ConfigDict


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None 
    

class EmailModel(BaseModel):
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class UserAuth(EmailModel):
    password: str 

class UserSchema(EmailModel):
    id: int 
    role_id: int 