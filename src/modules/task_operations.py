from dataclasses import dataclass
from typing import Annotated
from fastapi import Depends

from src.common.db_storage import DBStorageHandler, DBStorageHandlerDep
from src.common.models import Task

@dataclass
class TaskOperations:
    db_storage: DBStorageHandler

    # Get task by ID
    def get(self, id: int) -> Task:
        try:
            return self.db_storage.get_by_id(id, Task)
        except ValueError:
            raise ValueError(f"Task with id {id} not found!")
    
    # Get all tasks
    def get_all(self) -> list[Task]:
        return self.db_storage.get_all(Task)
    
    # Add a new task
    def add(self, task_data: dict) -> Task:
        task = Task(**task_data)
        self.db_storage.create(task)
        return task
    
    # Delete a task by ID
    def delete(self, id: int):
        try:
            self.db_storage.delete(id, Task)
        except ValueError:
            raise ValueError(f"Task with id {id} not found!")
    
    # Change the status of a task by ID
    def change_status(self, id: int):
        task = self.get(id)
        task.completed = not task.completed
        self.db_storage.update(id, task)


# Dependency to provide TaskOperations instance
def get_task_operations(db_storage: DBStorageHandlerDep) -> TaskOperations:
    return TaskOperations(db_storage)

TaskOperationsDep = Annotated[TaskOperations, Depends(get_task_operations)]