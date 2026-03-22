from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QTextDocument, QFont, QColor
from PyQt6.QtWidgets import QApplication
from datetime import date, datetime
from typing import List, Optional
import os

from ..storage.models import DailyStats, Task
from ..analytics.stats_calculator import WeeklyStats


class PDFExporter:
    @staticmethod
    def export_daily_report(stats: DailyStats, file_path: str) -> bool:
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)

            doc = QTextDocument()
            html = PDFExporter._generate_daily_html(stats)
            doc.setHtml(html)

            doc.print(printer)
            return True
        except Exception as e:
            print(f"PDF导出失败: {e}")
            return False

    @staticmethod
    def export_weekly_report(weekly_stats: WeeklyStats, file_path: str) -> bool:
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)

            doc = QTextDocument()
            html = PDFExporter._generate_weekly_html(weekly_stats)
            doc.setHtml(html)

            doc.print(printer)
            return True
        except Exception as e:
            print(f"PDF导出失败: {e}")
            return False

    @staticmethod
    def export_task_report(tasks: List[Task], file_path: str) -> bool:
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)

            doc = QTextDocument()
            html = PDFExporter._generate_tasks_html(tasks)
            doc.setHtml(html)

            doc.print(printer)
            return True
        except Exception as e:
            print(f"PDF导出失败: {e}")
            return False

    @staticmethod
    def _generate_daily_html(stats: DailyStats) -> str:
        work_hours = stats.work_seconds / 3600
        work_minutes = stats.work_seconds // 60
        break_minutes = stats.break_seconds // 60

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: "Microsoft YaHei", Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #e74c3c; text-align: center; }}
                h2 {{ color: #3498db; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
                .summary {{ background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .stat-item {{ margin: 10px 0; font-size: 14px; }}
                .stat-label {{ font-weight: bold; color: #555; }}
                .stat-value {{ color: #333; }}
                .highlight {{ color: #e74c3c; font-size: 24px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>🍅 番茄钟日报</h1>
            <h2>{stats.date.strftime("%Y年%m月%d日")}</h2>
            
            <div class="summary">
                <div class="stat-item">
                    <span class="stat-label">工作时长：</span>
                    <span class="stat-value highlight">{work_hours:.2f} 小时</span>
                    <span class="stat-value">（{work_minutes} 分钟）</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">休息时长：</span>
                    <span class="stat-value">{break_minutes} 分钟</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">完成番茄：</span>
                    <span class="stat-value highlight">{stats.pomodoros} 个</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">完成任务：</span>
                    <span class="stat-value">{stats.tasks} 个</span>
                </div>
            </div>
            
            <p style="text-align: center; color: #999; font-size: 12px;">
                报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </p>
        </body>
        </html>
        """

    @staticmethod
    def _generate_weekly_html(weekly_stats: WeeklyStats) -> str:
        daily_rows = ""
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        for stats in weekly_stats.daily_breakdown:
            day_name = weekdays[stats.date.weekday()]
            daily_rows += f"""
                <tr>
                    <td>{stats.date.strftime("%m/%d")} {day_name}</td>
                    <td>{stats.work_seconds // 60}</td>
                    <td>{stats.break_seconds // 60}</td>
                    <td>{stats.pomodoros_completed}</td>
                </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: "Microsoft YaHei", Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #e74c3c; text-align: center; }}
                h2 {{ color: #3498db; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
                .summary {{ background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .stat-item {{ margin: 10px 0; font-size: 14px; }}
                .stat-label {{ font-weight: bold; color: #555; }}
                .stat-value {{ color: #333; }}
                .highlight {{ color: #e74c3c; font-size: 24px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: center; }}
                th {{ background: #3498db; color: white; }}
                tr:nth-child(even) {{ background: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>🍅 番茄钟周报</h1>
            <h2>{weekly_stats.start_date.strftime("%Y年%m月%d日")} - {weekly_stats.end_date.strftime("%Y年%m月%d日")}</h2>
            
            <div class="summary">
                <div class="stat-item">
                    <span class="stat-label">总工作时长：</span>
                    <span class="stat-value highlight">{weekly_stats.total_work_hours:.2f} 小时</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">总休息时长：</span>
                    <span class="stat-value">{weekly_stats.total_break_hours:.2f} 小时</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">完成番茄：</span>
                    <span class="stat-value highlight">{weekly_stats.total_pomodoros} 个</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">日均工作：</span>
                    <span class="stat-value">{weekly_stats.average_daily_work_hours:.2f} 小时</span>
                </div>
            </div>
            
            <h3>每日明细</h3>
            <table>
                <tr>
                    <th>日期</th>
                    <th>工作(分钟)</th>
                    <th>休息(分钟)</th>
                    <th>番茄数</th>
                </tr>
                {daily_rows}
            </table>
            
            <p style="text-align: center; color: #999; font-size: 12px;">
                报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </p>
        </body>
        </html>
        """

    @staticmethod
    def _generate_tasks_html(tasks: List[Task]) -> str:
        task_rows = ""
        for task in tasks:
            status = "✓ 已归档" if task.status.value == "archived" else "进行中"
            task_rows += f"""
                <tr>
                    <td>{task.title}</td>
                    <td>{task.notes[:50] + "..." if len(task.notes) > 50 else task.notes}</td>
                    <td>{task.completed_pomodoros}/{task.estimated_pomodoros}</td>
                    <td>{status}</td>
                    <td>{task.created_at.strftime("%Y-%m-%d")}</td>
                </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: "Microsoft YaHei", Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #e74c3c; text-align: center; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                th {{ background: #3498db; color: white; }}
                tr:nth-child(even) {{ background: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>📋 任务列表报告</h1>
            
            <table>
                <tr>
                    <th>标题</th>
                    <th>备注</th>
                    <th>番茄进度</th>
                    <th>状态</th>
                    <th>创建日期</th>
                </tr>
                {task_rows}
            </table>
            
            <p style="text-align: center; color: #999; font-size: 12px;">
                报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                <br>共 {len(tasks)} 个任务
            </p>
        </body>
        </html>
        """
