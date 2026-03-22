import pytest
from datetime import datetime, timedelta
import tempfile
import os

from src.storage.database import Database
from src.storage.models import Task, TaskStatus, TimeEntry, PomodoroType, DailyStats


class TestDatabase:
    @pytest.fixture
    def db(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        db = Database(db_path)
        yield db
        os.unlink(db_path)

    def test_create_task(self, db):
        task = Task(
            id=None,
            title="测试任务",
            notes="这是一个测试",
            status=TaskStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            estimated_pomodoros=4,
        )
        created = db.create_task(task)

        assert created.id is not None
        assert created.title == "测试任务"
        assert created.notes == "这是一个测试"
        assert created.status == TaskStatus.ACTIVE

    def test_get_task(self, db):
        task = Task(
            id=None,
            title="获取测试",
            notes="",
            status=TaskStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        created = db.create_task(task)
        retrieved = db.get_task(created.id)

        assert retrieved is not None
        assert retrieved.title == "获取测试"

    def test_get_all_tasks(self, db):
        for i in range(3):
            task = Task(
                id=None,
                title=f"任务{i}",
                notes="",
                status=TaskStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.create_task(task)

        tasks = db.get_all_tasks()
        assert len(tasks) == 3

    def test_update_task(self, db):
        task = Task(
            id=None,
            title="原始标题",
            notes="",
            status=TaskStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        created = db.create_task(task)

        created.title = "更新后的标题"
        created.notes = "添加备注"
        updated = db.update_task(created)

        assert updated.title == "更新后的标题"
        assert updated.notes == "添加备注"

    def test_delete_task(self, db):
        task = Task(
            id=None,
            title="待删除任务",
            notes="",
            status=TaskStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        created = db.create_task(task)

        result = db.delete_task(created.id)
        assert result is True

        retrieved = db.get_task(created.id)
        assert retrieved is None

    def test_archive_task(self, db):
        task = Task(
            id=None,
            title="待归档任务",
            notes="",
            status=TaskStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        created = db.create_task(task)

        db.archive_task(created.id)
        retrieved = db.get_task(created.id)

        assert retrieved.status == TaskStatus.ARCHIVED

    def test_search_tasks(self, db):
        task1 = Task(
            id=None,
            title="Python开发",
            notes="使用Python进行开发",
            status=TaskStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        task2 = Task(
            id=None,
            title="Java开发",
            notes="使用Java进行开发",
            status=TaskStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.create_task(task1)
        db.create_task(task2)

        results = db.search_tasks("Python")
        assert len(results) == 1
        assert results[0].title == "Python开发"

    def test_create_time_entry(self, db):
        entry = TimeEntry(
            id=None,
            task_id=None,
            pomodoro_type=PomodoroType.WORK,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=25),
            duration_seconds=25 * 60,
            is_completed=True,
        )
        created = db.create_time_entry(entry)

        assert created.id is not None
        assert created.pomodoro_type == PomodoroType.WORK

    def test_get_time_entries_by_date(self, db):
        today = datetime.now().date()
        entry = TimeEntry(
            id=None,
            task_id=None,
            pomodoro_type=PomodoroType.WORK,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=25),
            duration_seconds=25 * 60,
            is_completed=True,
        )
        db.create_time_entry(entry)

        entries = db.get_time_entries_by_date(today)
        assert len(entries) == 1

    def test_daily_stats(self, db):
        today = datetime.now().date()
        stats = db.get_or_create_daily_stats(today)

        assert stats.id is not None
        assert stats.date == today

        stats.work_seconds = 3600
        stats.pomodoros_completed = 4
        updated = db.update_daily_stats(stats)

        assert updated.work_seconds == 3600
        assert updated.pomodoros_completed == 4
