# src/modules/task_operations.py

from dataclasses import dataclass
from typing import Annotated
from fastapi import Depends

from src.common.db_storage import DBStorageHandler, StorageDep
from src.common.models import Task

@dataclass
class TaskOperations:
    db_storage: DBStorageHandler[Task]

    def get(self, id: int) -> Task:
        """"Get a task by ID"""
        return self.db_storage.get_by_id(id, Task)
    

    def get_user_tasks(self, user_id: int) -> list[Task]:
        """Get all tasks for a specific user"""
        return self.db_storage.get_all_where(Task, Task.user_id == user_id)

    
    def add(self, task_data: dict) -> Task:
        """Create a new task"""
        task = Task(**task_data)
        return self.db_storage.create(task)
    
    
    def delete(self, id: int) -> None:
        """Delete a task by ID"""
        self.db_storage.delete(id, Task)
        
    
    def change_status(self, id: int):
        """Toggle the completion status of a task"""
        task = self.get(id)
        return self.db_storage.update(id, Task, {"completed": not task.completed})


def get_task_operations(db_storage: StorageDep) -> TaskOperations:
    """Dependency to get TaskOperations instance"""
    return TaskOperations(db_storage)

TaskOperationsDep = Annotated[TaskOperations, Depends(get_task_operations)]