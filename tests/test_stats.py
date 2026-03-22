import pytest
from datetime import date, timedelta, datetime
import tempfile
import os

from src.storage.database import Database
from src.storage.models import Task, TaskStatus, TimeEntry, PomodoroType, DailyStats
from src.analytics.stats_calculator import StatsCalculator


class TestStatsCalculator:
    @pytest.fixture
    def db(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        db = Database(db_path)
        yield db
        os.unlink(db_path)

    @pytest.fixture
    def calculator(self, db):
        return StatsCalculator(db)

    def test_get_daily_summary_empty(self, calculator, db):
        today = date.today()
        summary = calculator.get_daily_summary(today)

        assert summary.date == today
        assert summary.work_seconds == 0
        assert summary.pomodoros == 0

    def test_get_daily_summary_with_data(self, calculator, db):
        today = date.today()

        stats = db.get_or_create_daily_stats(today)
        stats.work_seconds = 3600
        stats.break_seconds = 600
        stats.pomodoros_completed = 4
        db.update_daily_stats(stats)

        entry = TimeEntry(
            id=None,
            task_id=None,
            pomodoro_type=PomodoroType.WORK,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=25),
            duration_seconds=1500,
            is_completed=True,
        )
        db.create_time_entry(entry)

        summary = calculator.get_daily_summary(today)

        assert summary.work_seconds == 3600
        assert summary.break_seconds == 600
        assert summary.pomodoros == 4
        assert len(summary.time_entries) == 1

    def test_get_weekly_stats(self, calculator, db):
        today = date.today()

        for i in range(7):
            d = today - timedelta(days=6 - i)
            stats = db.get_or_create_daily_stats(d)
            stats.work_seconds = 3600 * (i + 1)
            stats.pomodoros_completed = i + 1
            db.update_daily_stats(stats)

        weekly = calculator.get_weekly_stats(today)

        assert weekly.total_pomodoros == 28
        assert weekly.total_work_seconds == 3600 * 28
        assert len(weekly.daily_breakdown) == 7

    def test_get_weekly_stats_average(self, calculator, db):
        today = date.today()

        for i in range(7):
            d = today - timedelta(days=6 - i)
            stats = db.get_or_create_daily_stats(d)
            stats.work_seconds = 3600
            db.update_daily_stats(stats)

        weekly = calculator.get_weekly_stats(today)

        assert weekly.average_daily_work_hours == 1.0

    def test_get_hourly_distribution(self, calculator, db):
        today = date.today()

        for hour in [9, 10, 14, 15]:
            entry = TimeEntry(
                id=None,
                task_id=None,
                pomodoro_type=PomodoroType.WORK,
                start_time=datetime.now().replace(hour=hour, minute=0),
                end_time=datetime.now().replace(hour=hour, minute=25),
                duration_seconds=1500,
                is_completed=True,
            )
            db.create_time_entry(entry)

        distribution = calculator.get_hourly_distribution(today)

        assert distribution[9] == 1500
        assert distribution[10] == 1500
        assert distribution[14] == 1500
        assert distribution[15] == 1500
        assert distribution[8] == 0

    def test_get_productivity_score_empty(self, calculator, db):
        score = calculator.get_productivity_score()
        assert score == 0.0

    def test_get_productivity_score_with_data(self, calculator, db):
        today = date.today()

        stats = db.get_or_create_daily_stats(today)
        stats.work_seconds = 2 * 3600
        stats.pomodoros_completed = 4
        db.update_daily_stats(stats)

        score = calculator.get_productivity_score(today)

        assert 0 < score <= 100

    def test_get_monthly_stats(self, calculator, db):
        today = date.today()

        for i in range(1, 8):
            d = date(today.year, today.month, i)
            stats = db.get_or_create_daily_stats(d)
            stats.work_seconds = 3600
            stats.pomodoros_completed = 2
            db.update_daily_stats(stats)

        monthly = calculator.get_monthly_stats(today.year, today.month)

        assert monthly["total_pomodoros"] >= 14
        assert monthly["work_hours"] >= 7

    def test_weekly_stats_date_range(self, calculator, db):
        end_date = date(2024, 1, 7)
        weekly = calculator.get_weekly_stats(end_date)

        assert weekly.start_date == date(2024, 1, 1)
        assert weekly.end_date == date(2024, 1, 7)

    def test_daily_summary_work_hours(self, calculator, db):
        today = date.today()

        stats = db.get_or_create_daily_stats(today)
        stats.work_seconds = 5400
        db.update_daily_stats(stats)

        summary = calculator.get_daily_summary(today)

        assert summary.work_hours == 1.5
        assert summary.work_minutes == 90
