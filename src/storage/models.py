from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Union
from enum import Enum


class TaskStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class PomodoroType(Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


@dataclass
class Task:
    id: Optional[int]
    title: str
    notes: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    estimated_pomodoros: int = 0
    completed_pomodoros: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data.get("id"),
            title=data["title"],
            notes=data.get("notes", ""),
            status=TaskStatus(data.get("status", "active")),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"],
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data["updated_at"], str) else data["updated_at"],
            estimated_pomodoros=data.get("estimated_pomodoros", 0),
            completed_pomodoros=data.get("completed_pomodoros", 0),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "notes": self.notes,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "estimated_pomodoros": self.estimated_pomodoros,
            "completed_pomodoros": self.completed_pomodoros,
        }


@dataclass
class TimeEntry:
    id: Optional[int]
    task_id: Optional[int]
    pomodoro_type: PomodoroType
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: int
    is_completed: bool

    @classmethod
    def from_dict(cls, data: dict) -> "TimeEntry":
        return cls(
            id=data.get("id"),
            task_id=data.get("task_id"),
            pomodoro_type=PomodoroType(data["pomodoro_type"]),
            start_time=datetime.fromisoformat(data["start_time"]) if isinstance(data["start_time"], str) else data["start_time"],
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") and isinstance(data["end_time"], str) else data.get("end_time"),
            duration_seconds=data.get("duration_seconds", 0),
            is_completed=data.get("is_completed", False),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "pomodoro_type": self.pomodoro_type.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "is_completed": self.is_completed,
        }


@dataclass
class DailyStats:
    id: Optional[int]
    date: Union[date, datetime]
    work_seconds: int
    break_seconds: int
    pomodoros_completed: int
    tasks_completed: int

    @classmethod
    def from_dict(cls, data: dict) -> "DailyStats":
        date_val = data["date"]
        if isinstance(date_val, str):
            date_val = datetime.fromisoformat(date_val)
        # 转换为date对象
        if isinstance(date_val, datetime):
            date_val = date_val.date()
        return cls(
            id=data.get("id"),
            date=date_val,
            work_seconds=data.get("work_seconds", 0),
            break_seconds=data.get("break_seconds", 0),
            pomodoros_completed=data.get("pomodoros_completed", 0),
            tasks_completed=data.get("tasks_completed", 0),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "work_seconds": self.work_seconds,
            "break_seconds": self.break_seconds,
            "pomodoros_completed": self.pomodoros_completed,
            "tasks_completed": self.tasks_completed,
        }
