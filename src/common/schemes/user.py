from pydantic import BaseModel

class UserLoginScheme(BaseModel):
    username: str
    password: str
    remember_me: bool = False

class UserCreateScheme(BaseModel):
    username: str
    email: str
    password: str