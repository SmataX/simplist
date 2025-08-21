import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from src.common.db_storage import get_session, create_db_and_tables
from src.common.models import Task
from src.modules.task_operations import TaskOperationsDep

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

    