import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from src.common.db_storage import get_session, create_db_and_tables
from src.common.models import Task
from src.modules.task_operations import TaskOperationsDep
from src.server.routers import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request, task_operations: TaskOperationsDep):
    tasks = task_operations.get_all()

    return templates.TemplateResponse(
        request=request, name="index.html", context={"tasks":tasks}
    )

    
@app.websocket("/ws")
async def ws_task_actions(websocket: WebSocket, task_operations: TaskOperationsDep):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            try:
                if action == "add":
                    task: Task = task_operations.add({"content": data.get("content")})
                    await websocket.send_json({"status": 1, "action": "add", "id": task.id})
                elif action == "delete":
                    task_operations.delete(data.get("id"))
                    await websocket.send_json({"status": 1, "action": "delete", "id": data.get("id")})
                elif action == "update":
                    task_operations.change_status(data.get("id"))
                    await websocket.send_json({"status": 1, "action": "update", "id": data.get("id")})
                else:
                    await websocket.send_json({"status": 0, "error": f"Unknown action: {action}"})
            except Exception as e:
                await websocket.send_json({"status": 0, "action": "error", "error": str(e)})
    except:
        print("Client disconnected")
    