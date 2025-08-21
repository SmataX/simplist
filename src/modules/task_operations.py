from dataclasses import dataclass
from typing import Annotated
from fastapi import Depends

from src.common.db_storage import DBStorageHandler, DBStorageHandlerDep
from src.common.models import Task

@dataclass
class TaskOperations:
    db_storage: DBStorageHandler

    def get(self, id: int) -> Task:
        try:
            return self.db_storage.get_by_id(id, Task)
        except ValueError:
            raise ValueError(f"Task with id {id} not found!")
        
    def get_all(self) -> list[Task]:
        return self.db_storage.get_all(Task)
    
    def delete(self, id: int):
        try:
            self.db_storage.delete(id, Task)
        except ValueError:
            raise ValueError(f"Task with id {id} not found!")
        
    def change_status(self, id: int):
        task = self.get(id)
        task.completed = not task.completed
        self.db_storage.update(id, task)


def get_task_operations(db_storage: DBStorageHandlerDep) -> TaskOperations:
    return TaskOperations(db_storage)

TaskOperationsDep = Annotated[TaskOperations, Depends(get_task_operations)]