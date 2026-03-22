import sqlite3
from pathlib import Path
from datetime import datetime, date
from typing import Optional, List
from contextlib import contextmanager

from .models import Task, TaskStatus, TimeEntry, PomodoroType, DailyStats


class Database:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / ".pomodoro_workbench" / "data.db")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    estimated_pomodoros INTEGER DEFAULT 0,
                    completed_pomodoros INTEGER DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    pomodoro_type TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_seconds INTEGER DEFAULT 0,
                    is_completed INTEGER DEFAULT 0,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    work_seconds INTEGER DEFAULT 0,
                    break_seconds INTEGER DEFAULT 0,
                    pomodoros_completed INTEGER DEFAULT 0,
                    tasks_completed INTEGER DEFAULT 0
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_time_entries_start ON time_entries(start_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_time_entries_task ON time_entries(task_id)")
            conn.commit()

    def create_task(self, task: Task) -> Task:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO tasks (title, notes, status, created_at, updated_at, estimated_pomodoros, completed_pomodoros)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (task.title, task.notes, task.status.value, now, now, task.estimated_pomodoros, task.completed_pomodoros))
            task.id = cursor.lastrowid
            task.created_at = datetime.fromisoformat(now)
            task.updated_at = datetime.fromisoformat(now)
            conn.commit()
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return Task.from_dict(dict(row))
        return None

    def get_all_tasks(self, include_archived: bool = False) -> List[Task]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if include_archived:
                cursor.execute("SELECT * FROM tasks ORDER BY updated_at DESC")
            else:
                cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY updated_at DESC", (TaskStatus.ACTIVE.value,))
            return [Task.from_dict(dict(row)) for row in cursor.fetchall()]

    def update_task(self, task: Task) -> Task:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE tasks SET title = ?, notes = ?, status = ?, updated_at = ?,
                estimated_pomodoros = ?, completed_pomodoros = ?
                WHERE id = ?
            """, (task.title, task.notes, task.status.value, now, task.estimated_pomodoros, task.completed_pomodoros, task.id))
            task.updated_at = datetime.fromisoformat(now)
            conn.commit()
        return task

    def delete_task(self, task_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM time_entries WHERE task_id = ?", (task_id,))
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0

    def archive_task(self, task_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?", (TaskStatus.ARCHIVED.value, now, task_id))
            conn.commit()
            return cursor.rowcount > 0

    def search_tasks(self, query: str) -> List[Task]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE (title LIKE ? OR notes LIKE ?) AND status = ?
                ORDER BY updated_at DESC
            """, (f"%{query}%", f"%{query}%", TaskStatus.ACTIVE.value))
            return [Task.from_dict(dict(row)) for row in cursor.fetchall()]

    def create_time_entry(self, entry: TimeEntry) -> TimeEntry:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO time_entries (task_id, pomodoro_type, start_time, end_time, duration_seconds, is_completed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (entry.task_id, entry.pomodoro_type.value, entry.start_time.isoformat(),
                  entry.end_time.isoformat() if entry.end_time else None,
                  entry.duration_seconds, entry.is_completed))
            entry.id = cursor.lastrowid
            conn.commit()
        return entry

    def update_time_entry(self, entry: TimeEntry) -> TimeEntry:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE time_entries SET end_time = ?, duration_seconds = ?, is_completed = ?
                WHERE id = ?
            """, (entry.end_time.isoformat() if entry.end_time else None, entry.duration_seconds, entry.is_completed, entry.id))
            conn.commit()
        return entry

    def get_time_entries_by_date(self, target_date: date) -> List[TimeEntry]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            date_str = target_date.isoformat()
            cursor.execute("""
                SELECT * FROM time_entries 
                WHERE date(start_time) = ?
                ORDER BY start_time
            """, (date_str,))
            return [TimeEntry.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_time_entries_by_task(self, task_id: int) -> List[TimeEntry]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM time_entries WHERE task_id = ? ORDER BY start_time", (task_id,))
            return [TimeEntry.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_time_entries_by_range(self, start_date: date, end_date: date) -> List[TimeEntry]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM time_entries 
                WHERE date(start_time) >= ? AND date(start_time) <= ?
                ORDER BY start_time
            """, (start_date.isoformat(), end_date.isoformat()))
            return [TimeEntry.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_or_create_daily_stats(self, target_date: date) -> DailyStats:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            date_str = target_date.isoformat()
            cursor.execute("SELECT * FROM daily_stats WHERE date = ?", (date_str,))
            row = cursor.fetchone()
            if row:
                return DailyStats.from_dict(dict(row))
            stats = DailyStats(id=None, date=target_date, work_seconds=0, break_seconds=0, pomodoros_completed=0, tasks_completed=0)
            cursor.execute("""
                INSERT INTO daily_stats (date, work_seconds, break_seconds, pomodoros_completed, tasks_completed)
                VALUES (?, ?, ?, ?, ?)
            """, (date_str, 0, 0, 0, 0))
            stats.id = cursor.lastrowid
            conn.commit()
            return stats

    def update_daily_stats(self, stats: DailyStats) -> DailyStats:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE daily_stats SET work_seconds = ?, break_seconds = ?, pomodoros_completed = ?, tasks_completed = ?
                WHERE id = ?
            """, (stats.work_seconds, stats.break_seconds, stats.pomodoros_completed, stats.tasks_completed, stats.id))
            conn.commit()
        return stats

    def get_stats_by_range(self, start_date: date, end_date: date) -> List[DailyStats]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_stats 
                WHERE date >= ? AND date <= ?
                ORDER BY date
            """, (start_date.isoformat(), end_date.isoformat()))
            return [DailyStats.from_dict(dict(row)) for row in cursor.fetchall()]

    def increment_pomodoros(self, task_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET completed_pomodoros = completed_pomodoros + 1 WHERE id = ?", (task_id,))
            conn.commit()
