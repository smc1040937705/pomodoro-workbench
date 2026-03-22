from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox, QScrollArea
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath
from datetime import date, timedelta
from typing import List, Optional, Dict

from ..storage.database import Database
from ..storage.models import DailyStats
from .stats_calculator import StatsCalculator, WeeklyStats, DailySummary


class BarChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[tuple] = []
        self._title = ""
        self._y_label = ""
        self._bar_color = QColor("#3498db")
        self.setMinimumHeight(200)

    def set_data(self, data: List[tuple], title: str = "", y_label: str = ""):
        self._data = data
        self._title = title
        self._y_label = y_label
        self.update()

    def set_bar_color(self, color: QColor):
        self._bar_color = color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        margin_left = 60
        margin_right = 20
        margin_top = 40
        margin_bottom = 40

        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom

        painter.fillRect(self.rect(), QColor("#ffffff"))

        if self._title:
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(0, 10, width, 30, Qt.AlignmentFlag.AlignHCenter, self._title)

        if not self._data:
            painter.setFont(QFont("Arial", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无数据")
            return

        max_value = max(v for _, v in self._data) if self._data else 1
        if max_value == 0:
            max_value = 1

        painter.setPen(QPen(QColor("#cccccc"), 1))
        for i in range(5):
            y = margin_top + chart_height * i // 4
            painter.drawLine(margin_left, y, width - margin_right, y)
            value = max_value * (4 - i) // 4
            painter.setFont(QFont("Arial", 8))
            painter.drawText(5, y - 5, margin_left - 10, 20, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(value))

        bar_count = len(self._data)
        bar_width = min(40, (chart_width - bar_count * 10) // bar_count)
        spacing = (chart_width - bar_width * bar_count) // (bar_count + 1)

        for i, (label, value) in enumerate(self._data):
            x = margin_left + spacing + i * (bar_width + spacing)
            bar_height = int(value / max_value * chart_height) if max_value > 0 else 0
            y = margin_top + chart_height - bar_height

            painter.setBrush(QBrush(self._bar_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(x, y, bar_width, bar_height)

            painter.setPen(QPen(QColor("#333333")))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(x, margin_top + chart_height + 5, bar_width, 30, Qt.AlignmentFlag.AlignHCenter, str(label))

    def sizeHint(self):
        return self.minimumSize()


class LineChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[tuple] = []
        self._title = ""
        self._y_label = ""
        self._line_color = QColor("#e74c3c")
        self.setMinimumHeight(200)

    def set_data(self, data: List[tuple], title: str = "", y_label: str = ""):
        self._data = data
        self._title = title
        self._y_label = y_label
        self.update()

    def set_line_color(self, color: QColor):
        self._line_color = color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        margin_left = 60
        margin_right = 20
        margin_top = 40
        margin_bottom = 40

        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom

        painter.fillRect(self.rect(), QColor("#ffffff"))

        if self._title:
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(0, 10, width, 30, Qt.AlignmentFlag.AlignHCenter, self._title)

        if not self._data:
            painter.setFont(QFont("Arial", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无数据")
            return

        max_value = max(v for _, v in self._data) if self._data else 1
        if max_value == 0:
            max_value = 1

        painter.setPen(QPen(QColor("#cccccc"), 1))
        for i in range(5):
            y = margin_top + chart_height * i // 4
            painter.drawLine(margin_left, y, width - margin_right, y)
            value = max_value * (4 - i) // 4
            painter.setFont(QFont("Arial", 8))
            painter.drawText(5, y - 5, margin_left - 10, 20, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(value))

        point_count = len(self._data)
        if point_count < 2:
            return

        points = []
        for i, (label, value) in enumerate(self._data):
            x = margin_left + (i * chart_width // (point_count - 1)) if point_count > 1 else margin_left + chart_width // 2
            y = margin_top + chart_height - int(value / max_value * chart_height) if max_value > 0 else margin_top + chart_height
            points.append((x, y, label))

        path = QPainterPath()
        path.moveTo(points[0][0], points[0][1])
        for x, y, _ in points[1:]:
            path.lineTo(x, y)

        painter.setPen(QPen(self._line_color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        for x, y, _ in points:
            painter.setBrush(QBrush(self._line_color))
            painter.drawEllipse(x - 4, y - 4, 8, 8)

        painter.setPen(QPen(QColor("#333333")))
        painter.setFont(QFont("Arial", 8))
        for i, (x, y, label) in enumerate(points):
            if i % max(1, len(points) // 7) == 0:
                painter.drawText(x - 20, margin_top + chart_height + 5, 40, 30, Qt.AlignmentFlag.AlignHCenter, str(label))


class PieChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[tuple] = []
        self._title = ""
        self._colors = [QColor("#3498db"), QColor("#e74c3c"), QColor("#2ecc71"), QColor("#f39c12"), QColor("#9b59b6")]
        self.setMinimumSize(200, 200)

    def set_data(self, data: List[tuple], title: str = ""):
        self._data = data
        self._title = title
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        painter.fillRect(self.rect(), QColor("#ffffff"))

        if self._title:
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(0, 10, width, 30, Qt.AlignmentFlag.AlignHCenter, self._title)

        if not self._data:
            painter.setFont(QFont("Arial", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无数据")
            return

        total = sum(v for _, v in self._data)
        if total == 0:
            painter.setFont(QFont("Arial", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无数据")
            return

        center_x = width // 3
        center_y = height // 2 + 15
        radius = min(width // 3, height // 2 - 30)

        start_angle = 0
        for i, (label, value) in enumerate(self._data):
            if value == 0:
                continue

            span_angle = int(value * 360 * 16 / total)
            color = self._colors[i % len(self._colors)]

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.drawPie(center_x - radius, center_y - radius, radius * 2, radius * 2, start_angle, span_angle)

            start_angle += span_angle

        legend_x = width * 2 // 3
        legend_y = 50
        painter.setFont(QFont("Arial", 9))
        for i, (label, value) in enumerate(self._data):
            color = self._colors[i % len(self._colors)]
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(legend_x, legend_y + i * 25, 15, 15)

            painter.setPen(QPen(QColor("#333333")))
            percent = value * 100 / total if total > 0 else 0
            painter.drawText(legend_x + 20, legend_y + i * 25, 100, 15, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{label}: {percent:.1f}%")


class StatsViewWidget(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.calculator = StatsCalculator(db)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("统计周期:"))

        self.period_combo = QComboBox()
        self.period_combo.addItems(["今日", "本周", "本月"])
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        toolbar.addWidget(self.period_combo)

        toolbar.addStretch()

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._load_data)
        toolbar.addWidget(self.refresh_btn)

        layout.addLayout(toolbar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        summary_group = QGroupBox("概览")
        summary_layout = QVBoxLayout(summary_group)
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        scroll_layout.addWidget(summary_group)

        daily_chart_group = QGroupBox("每日专注时长（分钟）")
        daily_chart_layout = QVBoxLayout(daily_chart_group)
        self.daily_bar_chart = BarChartWidget()
        self.daily_bar_chart.set_bar_color(QColor("#3498db"))
        daily_chart_layout.addWidget(self.daily_bar_chart)
        scroll_layout.addWidget(daily_chart_group)

        pomodoro_chart_group = QGroupBox("番茄数趋势")
        pomodoro_chart_layout = QVBoxLayout(pomodoro_chart_group)
        self.pomodoro_line_chart = LineChartWidget()
        self.pomodoro_line_chart.set_line_color(QColor("#e74c3c"))
        pomodoro_chart_layout.addWidget(self.pomodoro_line_chart)
        scroll_layout.addWidget(pomodoro_chart_group)

        distribution_group = QGroupBox("时间分布")
        distribution_layout = QVBoxLayout(distribution_group)
        self.hourly_chart = BarChartWidget()
        self.hourly_chart.set_bar_color(QColor("#2ecc71"))
        distribution_layout.addWidget(self.hourly_chart)
        scroll_layout.addWidget(distribution_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def _on_period_changed(self):
        self._load_data()

    def _load_data(self):
        period = self.period_combo.currentText()

        if period == "今日":
            self._load_daily_stats()
        elif period == "本周":
            self._load_weekly_stats()
        else:
            self._load_monthly_stats()

    def _load_daily_stats(self):
        summary = self.calculator.get_daily_summary()
        work_hours = summary.work_seconds / 3600
        work_minutes = summary.work_seconds // 60

        self.summary_label.setText(
            f"工作时长: {work_hours:.2f} 小时 ({work_minutes} 分钟)\n"
            f"休息时长: {summary.break_seconds // 60} 分钟\n"
            f"完成番茄: {summary.pomodoros} 个\n"
            f"完成任务: {summary.tasks} 个"
        )

        hourly = self.calculator.get_hourly_distribution()
        hourly_data = [(f"{h}时", v // 60) for h, v in hourly.items() if v > 0]
        self.hourly_chart.set_data(hourly_data, "每小时工作时长（分钟）")

        self.daily_bar_chart.set_data([], "")
        self.pomodoro_line_chart.set_data([], "")

    def _load_weekly_stats(self):
        weekly = self.calculator.get_weekly_stats()

        self.summary_label.setText(
            f"本周工作时长: {weekly.total_work_hours:.2f} 小时\n"
            f"本周休息时长: {weekly.total_break_hours:.2f} 小时\n"
            f"完成番茄: {weekly.total_pomodoros} 个\n"
            f"日均工作: {weekly.average_daily_work_hours:.2f} 小时"
        )

        daily_data = []
        pomodoro_data = []
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]

        for i, stats in enumerate(weekly.daily_breakdown):
            day_name = weekdays[stats.date.weekday()]
            daily_data.append((day_name, stats.work_seconds // 60))
            pomodoro_data.append((day_name, stats.pomodoros_completed))

        self.daily_bar_chart.set_data(daily_data, "每日工作时长（分钟）")
        self.pomodoro_line_chart.set_data(pomodoro_data, "每日番茄数")

        hourly = self.calculator.get_hourly_distribution()
        hourly_data = [(f"{h}时", v // 60) for h, v in hourly.items() if v > 0]
        self.hourly_chart.set_data(hourly_data, "今日工作时段分布（分钟）")

    def _load_monthly_stats(self):
        today = date.today()
        monthly = self.calculator.get_monthly_stats(today.year, today.month)

        self.summary_label.setText(
            f"本月工作时长: {monthly['work_hours']:.2f} 小时\n"
            f"本月休息时长: {monthly['total_break_seconds'] / 3600:.2f} 小时\n"
            f"完成番茄: {monthly['total_pomodoros']} 个"
        )

        daily_data = []
        pomodoro_data = []
        for stats in monthly["daily_stats"]:
            day = stats.date.day
            daily_data.append((str(day), stats.work_seconds // 60))
            pomodoro_data.append((str(day), stats.pomodoros_completed))

        self.daily_bar_chart.set_data(daily_data[-14:], "近两周工作时长（分钟）")
        self.pomodoro_line_chart.set_data(pomodoro_data[-14:], "近两周番茄数")

        hourly = self.calculator.get_hourly_distribution()
        hourly_data = [(f"{h}时", v // 60) for h, v in hourly.items() if v > 0]
        self.hourly_chart.set_data(hourly_data, "今日工作时段分布（分钟）")

    def refresh(self):
        self._load_data()
