# src/server/routers/auth.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from typing import Annotated
from src.common.db_storage import get_session
from src.common.schemes import LoginForm, RegisterForm
from src.modules.auth_operations import login_user, register_user, get_current_user


templates = Jinja2Templates(directory="templates")
router = APIRouter()

DBSession = Annotated[Session, Depends(get_session)]

@router.get("/login")
async def login_get(request: Request, db_session=Depends(get_session)):
    if get_current_user(request, db_session):
        return RedirectResponse(url="/tasks", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_post(request: Request, db_session: DBSession, form: LoginForm):
    user = login_user(request, db_session, form)

    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"}, status_code=400)

    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse(url="/tasks", status_code=302)



@router.get("/register")
async def register_get(request: Request, db_session=Depends(get_session)):
    if get_current_user(request, db_session):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_post(request: Request, db_session: DBSession, form: RegisterForm):
    register_user(request, db_session, form)
    return RedirectResponse(url="/login", status_code=302)



@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)