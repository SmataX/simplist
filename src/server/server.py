import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, WebSocket
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


clinets = []

@app.get("/")
async def root(request: Request, task_operations: TaskOperationsDep):
    tasks = task_operations.get_all()

    return templates.TemplateResponse(
        request=request, name="index.html", context={"tasks":tasks}
    )


@app.websocket("/ws/add")
async def ws_add_task(websocket: WebSocket, task_operations: TaskOperationsDep):
    await websocket.accept()
    clinets.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            task_operations.add(data)
    except:
        clinets.remove(websocket)


@app.websocket("/ws/delete")
async def ws_delete_task(websocket: WebSocket, task_operations: TaskOperationsDep):
    await websocket.accept()
    clinets.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                task_operations.delete(data.get("id"))
                await websocket.send_json({"status": 1, "id": data.get("id")})
            except Exception as e:
                await websocket.send_json({"status": 0, "error": str(e)})
    except:
        clinets.remove(websocket)


    

    