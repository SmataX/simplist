from pydantic import BaseModel
from fastapi import Form, Depends
from typing import Annotated

class UserLoginScheme(BaseModel):
    username: str
    password: str
    remember_me: bool = False

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
        remember_me: bool = Form(False)
    ):
        return cls(username=username, password=password, remember_me=remember_me)

class UserCreateScheme(BaseModel):
    username: str
    email: str
    password: str

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
    ):
        return cls(username=username, email=email, password=password)
    


LoginForm = Annotated[UserLoginScheme, Depends(UserLoginScheme.as_form)]
RegisterForm = Annotated[UserCreateScheme, Depends(UserCreateScheme.as_form)]