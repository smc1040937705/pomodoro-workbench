import csv
from datetime import date, datetime
from typing import List, Optional
from pathlib import Path

from ..storage.models import DailyStats, TimeEntry, Task
from ..analytics.stats_calculator import WeeklyStats


class CSVExporter:
    @staticmethod
    def export_daily_stats(stats_list: List[DailyStats], file_path: str) -> bool:
        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["日期", "工作时长(分钟)", "休息时长(分钟)", "番茄数", "完成任务数"])

                for stats in stats_list:
                    writer.writerow([
                        stats.date.isoformat(),
                        stats.work_seconds // 60,
                        stats.break_seconds // 60,
                        stats.pomodoros_completed,
                        stats.tasks_completed,
                    ])
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False

    @staticmethod
    def export_time_entries(entries: List[TimeEntry], file_path: str) -> bool:
        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "任务ID", "类型", "开始时间", "结束时间", "时长(秒)", "是否完成"])

                for entry in entries:
                    writer.writerow([
                        entry.id,
                        entry.task_id or "",
                        entry.pomodoro_type.value,
                        entry.start_time.isoformat(),
                        entry.end_time.isoformat() if entry.end_time else "",
                        entry.duration_seconds,
                        "是" if entry.is_completed else "否",
                    ])
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False

    @staticmethod
    def export_tasks(tasks: List[Task], file_path: str) -> bool:
        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "标题", "备注", "状态", "创建时间", "更新时间", "预估番茄", "完成番茄"])

                for task in tasks:
                    writer.writerow([
                        task.id,
                        task.title,
                        task.notes,
                        task.status.value,
                        task.created_at.isoformat(),
                        task.updated_at.isoformat(),
                        task.estimated_pomodoros,
                        task.completed_pomodoros,
                    ])
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False

    @staticmethod
    def export_weekly_report(weekly_stats: WeeklyStats, file_path: str) -> bool:
        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["周报统计"])
                writer.writerow(["开始日期", weekly_stats.start_date.isoformat()])
                writer.writerow(["结束日期", weekly_stats.end_date.isoformat()])
                writer.writerow(["总工作时长(小时)", f"{weekly_stats.total_work_hours:.2f}"])
                writer.writerow(["总休息时长(小时)", f"{weekly_stats.total_break_hours:.2f}"])
                writer.writerow(["完成番茄数", weekly_stats.total_pomodoros])
                writer.writerow(["完成任务数", weekly_stats.total_tasks])
                writer.writerow(["日均工作时长(小时)", f"{weekly_stats.average_daily_work_hours:.2f}"])
                writer.writerow([])

                writer.writerow(["每日明细"])
                writer.writerow(["日期", "工作时长(分钟)", "休息时长(分钟)", "番茄数", "完成任务数"])

                for stats in weekly_stats.daily_breakdown:
                    writer.writerow([
                        stats.date.isoformat(),
                        stats.work_seconds // 60,
                        stats.break_seconds // 60,
                        stats.pomodoros_completed,
                        stats.tasks_completed,
                    ])
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
