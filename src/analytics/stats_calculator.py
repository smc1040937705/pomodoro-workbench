from dataclasses import dataclass
from datetime import date, timedelta, datetime
from typing import List, Dict, Optional
from ..storage.database import Database
from ..storage.models import DailyStats, TimeEntry, PomodoroType


@dataclass
class WeeklyStats:
    start_date: date
    end_date: date
    total_work_seconds: int
    total_break_seconds: int
    total_pomodoros: int
    total_tasks: int
    daily_breakdown: List[DailyStats]

    @property
    def total_work_hours(self) -> float:
        return self.total_work_seconds / 3600

    @property
    def total_break_hours(self) -> float:
        return self.total_break_seconds / 3600

    @property
    def average_daily_work_hours(self) -> float:
        return self.total_work_hours / 7 if self.daily_breakdown else 0


@dataclass
class DailySummary:
    date: date
    work_seconds: int
    break_seconds: int
    pomodoros: int
    tasks: int
    time_entries: List[TimeEntry]

    @property
    def work_hours(self) -> float:
        return self.work_seconds / 3600

    @property
    def work_minutes(self) -> int:
        return self.work_seconds // 60


class StatsCalculator:
    def __init__(self, db: Database):
        self.db = db

    def get_daily_summary(self, target_date: Optional[date] = None) -> DailySummary:
        if target_date is None:
            target_date = date.today()

        stats = self.db.get_or_create_daily_stats(target_date)
        entries = self.db.get_time_entries_by_date(target_date)

        return DailySummary(
            date=target_date,
            work_seconds=stats.work_seconds,
            break_seconds=stats.break_seconds,
            pomodoros=stats.pomodoros_completed,
            tasks=stats.tasks_completed,
            time_entries=entries,
        )

    def get_weekly_stats(self, end_date: Optional[date] = None) -> WeeklyStats:
        if end_date is None:
            end_date = date.today()

        start_date = end_date - timedelta(days=6)
        stats_list = self.db.get_stats_by_range(start_date, end_date)

        all_dates = []
        current = start_date
        while current <= end_date:
            all_dates.append(current)
            current += timedelta(days=1)

        stats_by_date = {s.date: s for s in stats_list}
        full_breakdown = []
        for d in all_dates:
            if d in stats_by_date:
                full_breakdown.append(stats_by_date[d])
            else:
                full_breakdown.append(DailyStats(
                    id=None,
                    date=d,
                    work_seconds=0,
                    break_seconds=0,
                    pomodoros_completed=0,
                    tasks_completed=0,
                ))

        total_work = sum(s.work_seconds for s in full_breakdown)
        total_break = sum(s.break_seconds for s in full_breakdown)
        total_pomodoros = sum(s.pomodoros_completed for s in full_breakdown)
        total_tasks = sum(s.tasks_completed for s in full_breakdown)

        return WeeklyStats(
            start_date=start_date,
            end_date=end_date,
            total_work_seconds=total_work,
            total_break_seconds=total_break,
            total_pomodoros=total_pomodoros,
            total_tasks=total_tasks,
            daily_breakdown=full_breakdown,
        )

    def get_monthly_stats(self, year: int, month: int) -> Dict:
        from calendar import monthrange
        _, days_in_month = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, days_in_month)

        stats_list = self.db.get_stats_by_range(start_date, end_date)

        total_work = sum(s.work_seconds for s in stats_list)
        total_break = sum(s.break_seconds for s in stats_list)
        total_pomodoros = sum(s.pomodoros_completed for s in stats_list)

        return {
            "year": year,
            "month": month,
            "total_work_seconds": total_work,
            "total_break_seconds": total_break,
            "total_pomodoros": total_pomodoros,
            "work_hours": total_work / 3600,
            "daily_stats": stats_list,
        }

    def get_hourly_distribution(self, target_date: Optional[date] = None) -> Dict[int, int]:
        if target_date is None:
            target_date = date.today()

        entries = self.db.get_time_entries_by_date(target_date)
        hourly_work: Dict[int, int] = {h: 0 for h in range(24)}

        for entry in entries:
            if entry.pomodoro_type == PomodoroType.WORK:
                hour = entry.start_time.hour
                hourly_work[hour] += entry.duration_seconds

        return hourly_work

    def get_productivity_score(self, target_date: Optional[date] = None) -> float:
        summary = self.get_daily_summary(target_date)
        if summary.pomodoros == 0:
            return 0.0

        expected_pomodoros = 8
        expected_work_minutes = 25 * expected_pomodoros

        actual_work_minutes = summary.work_minutes
        pomodoro_score = min(summary.pomodoros / expected_pomodoros, 1.0) * 50
        time_score = min(actual_work_minutes / expected_work_minutes, 1.0) * 50

        return pomodoro_score + time_score
