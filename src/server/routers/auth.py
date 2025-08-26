from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.common.db_storage import get_session


templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/auth")

@router.get("/login")
async def login_get(request: Request, db_session=Depends(get_session)):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_post():
    pass

@router.get("/register")
async def register_get(request: Request, db_session=Depends(get_session)):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_post():
    pass