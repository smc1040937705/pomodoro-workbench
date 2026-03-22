from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar,
    QComboBox, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional

from ..timer.qt_timer import QtPomodoroTimer
from ..timer.pomodoro_timer import TimerState, PomodoroPhase, TimerConfig
from ..storage.database import Database
from ..storage.models import TimeEntry, PomodoroType, DailyStats
from datetime import datetime, date


class TimerDisplay(QWidget):
    start_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    resume_clicked = pyqtSignal()
    skip_clicked = pyqtSignal()
    reset_clicked = pyqtSignal()

    def __init__(self, timer: QtPomodoroTimer, db: Database, parent=None):
        super().__init__(parent)
        self.timer = timer
        self.db = db
        self._current_task_id: Optional[int] = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.phase_label = QLabel("工作")
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.phase_label.setFont(font)
        layout.addWidget(self.phase_label)

        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_font = QFont()
        time_font.setPointSize(48)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        layout.addWidget(self.time_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)

        self.task_combo = QComboBox()
        self.task_combo.setPlaceholderText("选择任务（可选）")
        self.task_combo.setMinimumWidth(200)
        layout.addWidget(self.task_combo)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_btn = QPushButton("开始")
        self.start_btn.setFixedWidth(80)
        self.start_btn.clicked.connect(self._on_start)
        btn_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setFixedWidth(80)
        self.pause_btn.clicked.connect(self._on_pause)
        self.pause_btn.setVisible(False)
        btn_layout.addWidget(self.pause_btn)

        self.resume_btn = QPushButton("继续")
        self.resume_btn.setFixedWidth(80)
        self.resume_btn.clicked.connect(self._on_resume)
        self.resume_btn.setVisible(False)
        btn_layout.addWidget(self.resume_btn)

        self.skip_btn = QPushButton("跳过")
        self.skip_btn.setFixedWidth(80)
        self.skip_btn.clicked.connect(self._on_skip)
        btn_layout.addWidget(self.skip_btn)

        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFixedWidth(80)
        self.reset_btn.clicked.connect(self._on_reset)
        btn_layout.addWidget(self.reset_btn)

        layout.addLayout(btn_layout)

        self.pomodoro_count_label = QLabel("今日完成: 0 个番茄")
        self.pomodoro_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.pomodoro_count_label)

        layout.addStretch()

    def _connect_signals(self):
        self.timer.tick.connect(self._on_tick)
        self.timer.state_changed.connect(self._on_state_changed)
        self.timer.phase_changed.connect(self._on_phase_changed)
        self.timer.phase_completed.connect(self._on_phase_completed)
        self.timer.pomodoro_completed.connect(self._on_pomodoro_completed)

    def _on_tick(self, remaining: int, elapsed: int):
        self.time_label.setText(self.timer.format_time(remaining))
        self.progress_bar.setValue(int(self.timer.get_progress_percent()))

    def _on_state_changed(self, state: TimerState):
        if state == TimerState.IDLE:
            self.start_btn.setVisible(True)
            self.pause_btn.setVisible(False)
            self.resume_btn.setVisible(False)
        elif state == TimerState.RUNNING:
            self.start_btn.setVisible(False)
            self.pause_btn.setVisible(True)
            self.resume_btn.setVisible(False)
        elif state == TimerState.PAUSED:
            self.start_btn.setVisible(False)
            self.pause_btn.setVisible(False)
            self.resume_btn.setVisible(True)

    def _on_phase_changed(self, phase: PomodoroPhase):
        self._update_phase_label(phase)
        self.time_label.setText(self.timer.format_time(self.timer.remaining_seconds))
        self.progress_bar.setValue(0)

    def _on_phase_completed(self, phase: PomodoroPhase, start_time: datetime, end_time: datetime, is_completed: bool):
        self._save_time_entry(phase, start_time, end_time, is_completed)

    def _on_pomodoro_completed(self, count: int):
        self._update_pomodoro_count()
        if self._current_task_id:
            self.db.increment_pomodoros(self._current_task_id)

    def _update_phase_label(self, phase: PomodoroPhase):
        phase_names = {
            PomodoroPhase.WORK: "工作",
            PomodoroPhase.SHORT_BREAK: "短休息",
            PomodoroPhase.LONG_BREAK: "长休息",
        }
        self.phase_label.setText(phase_names.get(phase, "工作"))

        colors = {
            PomodoroPhase.WORK: "#e74c3c",
            PomodoroPhase.SHORT_BREAK: "#27ae60",
            PomodoroPhase.LONG_BREAK: "#3498db",
        }
        self.phase_label.setStyleSheet(f"color: {colors.get(phase, '#333')};")

    def _on_start(self):
        task_id = self.task_combo.currentData()
        self._current_task_id = task_id
        self.timer.start(task_id)
        self.start_clicked.emit()

    def _on_pause(self):
        self.timer.pause()
        self.pause_clicked.emit()

    def _on_resume(self):
        self.timer.resume()
        self.resume_clicked.emit()

    def _on_skip(self):
        self.timer.skip()
        self.skip_clicked.emit()

    def _on_reset(self):
        self.timer.reset()
        self.time_label.setText(self.timer.format_time(self.timer.remaining_seconds))
        self.progress_bar.setValue(0)
        self.reset_clicked.emit()

    def _save_time_entry(self, phase: PomodoroPhase, start_time: datetime, end_time: datetime, is_completed: bool):
        pomodoro_type_map = {
            PomodoroPhase.WORK: PomodoroType.WORK,
            PomodoroPhase.SHORT_BREAK: PomodoroType.SHORT_BREAK,
            PomodoroPhase.LONG_BREAK: PomodoroType.LONG_BREAK,
        }
        duration = int((end_time - start_time).total_seconds())
        entry = TimeEntry(
            id=None,
            task_id=self._current_task_id,
            pomodoro_type=pomodoro_type_map[phase],
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            is_completed=is_completed,
        )
        self.db.create_time_entry(entry)
        self._update_daily_stats(phase, duration, is_completed)

    def _update_daily_stats(self, phase: PomodoroPhase, duration: int, is_completed: bool):
        today = date.today()
        stats = self.db.get_or_create_daily_stats(today)
        if phase == PomodoroPhase.WORK:
            stats.work_seconds += duration
            if is_completed:
                stats.pomodoros_completed += 1
        else:
            stats.break_seconds += duration
        self.db.update_daily_stats(stats)

    def _update_pomodoro_count(self):
        today = date.today()
        stats = self.db.get_or_create_daily_stats(today)
        self.pomodoro_count_label.setText(f"今日完成: {stats.pomodoros_completed} 个番茄")

    def load_tasks(self, tasks):
        self.task_combo.clear()
        self.task_combo.addItem("无关联任务", None)
        for task in tasks:
            self.task_combo.addItem(f"{task.title} [{task.completed_pomodoros}/{task.estimated_pomodoros}]", task.id)

    def set_current_task(self, task_id: Optional[int]):
        self._current_task_id = task_id
        for i in range(self.task_combo.count()):
            if self.task_combo.itemData(i) == task_id:
                self.task_combo.setCurrentIndex(i)
                break
        self.timer.set_current_task(task_id)

    def refresh_stats(self):
        self._update_pomodoro_count()

    def get_selected_task_id(self) -> Optional[int]:
        return self.task_combo.currentData()

    def update_time_display(self):
        """更新计时器显示的时间"""
        self.time_label.setText(self.timer.format_time(self.timer.remaining_seconds))
