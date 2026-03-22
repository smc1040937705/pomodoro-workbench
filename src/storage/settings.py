from PyQt6.QtCore import QSettings, QByteArray
from dataclasses import dataclass
from typing import Optional, List
import json


@dataclass
class TimerConfig:
    work_duration: int = 25
    short_break_duration: int = 5
    long_break_duration: int = 15
    pomodoros_until_long_break: int = 4
    auto_start_break: bool = False
    auto_start_work: bool = False
    sound_enabled: bool = True
    notification_enabled: bool = True


class SettingsManager:
    def __init__(self):
        self.settings = QSettings("PomodoroWorkbench", "PomodoroWorkbench")

    def save_window_geometry(self, geometry: QByteArray):
        self.settings.setValue("window/geometry", geometry)

    def load_window_geometry(self) -> Optional[QByteArray]:
        return self.settings.value("window/geometry")

    def save_window_state(self, state: QByteArray):
        self.settings.setValue("window/state", state)

    def load_window_state(self) -> Optional[QByteArray]:
        return self.settings.value("window/state")

    def save_current_view(self, view_index: int):
        self.settings.setValue("window/current_view", view_index)

    def load_current_view(self) -> int:
        return int(self.settings.value("window/current_view", 0))

    def save_timer_config(self, config: TimerConfig):
        self.settings.setValue("timer/work_duration", config.work_duration)
        self.settings.setValue("timer/short_break_duration", config.short_break_duration)
        self.settings.setValue("timer/long_break_duration", config.long_break_duration)
        self.settings.setValue("timer/pomodoros_until_long_break", config.pomodoros_until_long_break)
        self.settings.setValue("timer/auto_start_break", config.auto_start_break)
        self.settings.setValue("timer/auto_start_work", config.auto_start_work)
        self.settings.setValue("timer/sound_enabled", config.sound_enabled)
        self.settings.setValue("timer/notification_enabled", config.notification_enabled)

    def load_timer_config(self) -> TimerConfig:
        return TimerConfig(
            work_duration=int(self.settings.value("timer/work_duration", 25)),
            short_break_duration=int(self.settings.value("timer/short_break_duration", 5)),
            long_break_duration=int(self.settings.value("timer/long_break_duration", 15)),
            pomodoros_until_long_break=int(self.settings.value("timer/pomodoros_until_long_break", 4)),
            auto_start_break=bool(self.settings.value("timer/auto_start_break", False)),
            auto_start_work=bool(self.settings.value("timer/auto_start_work", False)),
            sound_enabled=bool(self.settings.value("timer/sound_enabled", True)),
            notification_enabled=bool(self.settings.value("timer/notification_enabled", True)),
        )

    def save_recent_tasks(self, task_ids: List[int]):
        self.settings.setValue("recent_tasks", json.dumps(task_ids))

    def load_recent_tasks(self) -> List[int]:
        data = self.settings.value("recent_tasks", "[]")
        return json.loads(data) if isinstance(data, str) else []

    def save_last_task_id(self, task_id: Optional[int]):
        self.settings.setValue("last_task_id", task_id if task_id else -1)

    def load_last_task_id(self) -> Optional[int]:
        task_id = self.settings.value("last_task_id", -1)
        return int(task_id) if int(task_id) > 0 else None

    def save_tray_minimize(self, minimize_to_tray: bool):
        self.settings.setValue("window/minimize_to_tray", minimize_to_tray)

    def load_tray_minimize(self) -> bool:
        return bool(self.settings.value("window/minimize_to_tray", True))
