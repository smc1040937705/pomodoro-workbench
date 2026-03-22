import pytest
import tempfile
import os
from datetime import date, datetime

from src.storage.models import DailyStats, Task, TaskStatus, TimeEntry, PomodoroType
from src.analytics.csv_exporter import CSVExporter
from src.analytics.pdf_exporter import PDFExporter
from src.analytics.stats_calculator import WeeklyStats


class TestCSVExporter:
    def test_export_daily_stats(self):
        stats_list = [
            DailyStats(id=1, date=date(2024, 1, 1), work_seconds=3600, break_seconds=300, pomodoros_completed=4, tasks_completed=2),
            DailyStats(id=2, date=date(2024, 1, 2), work_seconds=7200, break_seconds=600, pomodoros_completed=8, tasks_completed=3),
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8-sig") as f:
            file_path = f.name

        try:
            result = CSVExporter.export_daily_stats(stats_list, file_path)
            assert result is True

            with open(file_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
                assert "日期" in content
                assert "工作时长(分钟)" in content
                assert "2024-01-01" in content
                assert "60" in content
        finally:
            os.unlink(file_path)

    def test_export_tasks(self):
        tasks = [
            Task(id=1, title="任务1", notes="备注1", status=TaskStatus.ACTIVE, created_at=datetime.now(), updated_at=datetime.now(), estimated_pomodoros=4, completed_pomodoros=2),
            Task(id=2, title="任务2", notes="备注2", status=TaskStatus.ARCHIVED, created_at=datetime.now(), updated_at=datetime.now(), estimated_pomodoros=2, completed_pomodoros=2),
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8-sig") as f:
            file_path = f.name

        try:
            result = CSVExporter.export_tasks(tasks, file_path)
            assert result is True

            with open(file_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
                assert "标题" in content
                assert "任务1" in content
                assert "任务2" in content
        finally:
            os.unlink(file_path)

    def test_export_time_entries(self):
        entries = [
            TimeEntry(id=1, task_id=1, pomodoro_type=PomodoroType.WORK, start_time=datetime(2024, 1, 1, 9, 0), end_time=datetime(2024, 1, 1, 9, 25), duration_seconds=1500, is_completed=True),
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8-sig") as f:
            file_path = f.name

        try:
            result = CSVExporter.export_time_entries(entries, file_path)
            assert result is True

            with open(file_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
                assert "类型" in content
                assert "work" in content
        finally:
            os.unlink(file_path)

    def test_export_weekly_report(self):
        weekly = WeeklyStats(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
            total_work_seconds=3600 * 7,
            total_break_seconds=1800 * 7,
            total_pomodoros=28,
            total_tasks=10,
            daily_breakdown=[
                DailyStats(id=None, date=date(2024, 1, 1), work_seconds=3600, break_seconds=1800, pomodoros_completed=4, tasks_completed=2),
            ],
        )

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8-sig") as f:
            file_path = f.name

        try:
            result = CSVExporter.export_weekly_report(weekly, file_path)
            assert result is True

            with open(file_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
                assert "周报统计" in content
                assert "2024-01-01" in content
        finally:
            os.unlink(file_path)


class TestPDFExporter:
    def test_export_daily_report(self, qapp):
        from src.analytics.stats_calculator import DailySummary

        summary = DailySummary(
            date=date(2024, 1, 1),
            work_seconds=3600,
            break_seconds=600,
            pomodoros=4,
            tasks=2,
            time_entries=[],
        )

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            file_path = f.name

        try:
            result = PDFExporter.export_daily_report(summary, file_path)
            assert result is True

            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0
        finally:
            os.unlink(file_path)

    def test_export_weekly_report(self, qapp):
        weekly = WeeklyStats(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
            total_work_seconds=3600 * 7,
            total_break_seconds=1800 * 7,
            total_pomodoros=28,
            total_tasks=10,
            daily_breakdown=[
                DailyStats(id=None, date=date(2024, 1, i), work_seconds=3600, break_seconds=1800, pomodoros_completed=4, tasks_completed=2)
                for i in range(1, 8)
            ],
        )

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            file_path = f.name

        try:
            result = PDFExporter.export_weekly_report(weekly, file_path)
            assert result is True

            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0
        finally:
            os.unlink(file_path)

    def test_export_task_report(self, qapp):
        tasks = [
            Task(id=1, title="任务1", notes="这是一个测试任务的备注", status=TaskStatus.ACTIVE, created_at=datetime.now(), updated_at=datetime.now(), estimated_pomodoros=4, completed_pomodoros=2),
        ]

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            file_path = f.name

        try:
            result = PDFExporter.export_task_report(tasks, file_path)
            assert result is True

            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0
        finally:
            os.unlink(file_path)
