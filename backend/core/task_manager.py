import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Any


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    def __init__(
        self,
        name: str,
        task_type: str,
        params: Optional[dict] = None,
        priority: int = 0,
    ):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.task_type = task_type
        self.params = params or {}
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result: Any = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "task_type": self.task_type,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskManager:
    def __init__(self, max_concurrent: int = 3):
        self.tasks: dict[str, Task] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.handlers: dict[str, callable] = {}

    def register_handler(self, task_type: str, handler: callable):
        self.handlers[task_type] = handler

    async def submit_task(
        self, name: str, task_type: str, params: Optional[dict] = None
    ) -> Task:
        task = Task(name=name, task_type=task_type, params=params)
        self.tasks[task.id] = task
        asyncio.create_task(self._run_task(task))
        return task

    async def _run_task(self, task: Task):
        async with self.semaphore:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()

            handler = self.handlers.get(task.task_type)
            if not handler:
                task.status = TaskStatus.FAILED
                task.error = f"No handler for task type: {task.task_type}"
                task.completed_at = datetime.now()
                return

            try:
                task.result = await handler(task.params)
                task.status = TaskStatus.COMPLETED
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
            finally:
                task.completed_at = datetime.now()

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> list[dict]:
        return [t.to_dict() for t in self.tasks.values()]

    def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            return True
        return False

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        now = datetime.now()
        to_remove = []
        for tid, task in self.tasks.items():
            if task.completed_at:
                age = (now - task.completed_at).total_seconds() / 3600
                if age > max_age_hours:
                    to_remove.append(tid)
        for tid in to_remove:
            del self.tasks[tid]
