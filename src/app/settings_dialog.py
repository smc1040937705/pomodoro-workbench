from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox,
    QCheckBox, QGroupBox, QFileDialog, QMessageBox, QDialog, QTabWidget,
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..timer.pomodoro_timer import TimerConfig
from ..storage.settings import TimerConfig as SettingsTimerConfig


class SettingsDialog(QDialog):
    settings_changed = pyqtSignal(object)

    def __init__(self, current_config: SettingsTimerConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(400)
        self._config = current_config
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        timer_group = QGroupBox("计时器设置")
        timer_layout = QVBoxLayout(timer_group)

        work_layout = QHBoxLayout()
        work_layout.addWidget(QLabel("工作时长(分钟):"))
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 120)
        self.work_spin.setValue(self._config.work_duration)
        work_layout.addWidget(self.work_spin)
        work_layout.addStretch()
        timer_layout.addLayout(work_layout)

        short_break_layout = QHBoxLayout()
        short_break_layout.addWidget(QLabel("短休息时长(分钟):"))
        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 30)
        self.short_break_spin.setValue(self._config.short_break_duration)
        short_break_layout.addWidget(self.short_break_spin)
        short_break_layout.addStretch()
        timer_layout.addLayout(short_break_layout)

        long_break_layout = QHBoxLayout()
        long_break_layout.addWidget(QLabel("长休息时长(分钟):"))
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 60)
        self.long_break_spin.setValue(self._config.long_break_duration)
        long_break_layout.addWidget(self.long_break_spin)
        long_break_layout.addStretch()
        timer_layout.addLayout(long_break_layout)

        pomodoros_layout = QHBoxLayout()
        pomodoros_layout.addWidget(QLabel("长休息间隔(番茄数):"))
        self.pomodoros_spin = QSpinBox()
        self.pomodoros_spin.setRange(2, 10)
        self.pomodoros_spin.setValue(self._config.pomodoros_until_long_break)
        pomodoros_layout.addWidget(self.pomodoros_spin)
        pomodoros_layout.addStretch()
        timer_layout.addLayout(pomodoros_layout)

        layout.addWidget(timer_group)

        auto_group = QGroupBox("自动开始")
        auto_layout = QVBoxLayout(auto_group)

        self.auto_break_check = QCheckBox("自动开始休息")
        self.auto_break_check.setChecked(self._config.auto_start_break)
        auto_layout.addWidget(self.auto_break_check)

        self.auto_work_check = QCheckBox("自动开始下一个番茄")
        self.auto_work_check.setChecked(self._config.auto_start_work)
        auto_layout.addWidget(self.auto_work_check)

        layout.addWidget(auto_group)

        notif_group = QGroupBox("通知")
        notif_layout = QVBoxLayout(notif_group)

        self.sound_check = QCheckBox("启用声音提醒")
        self.sound_check.setChecked(self._config.sound_enabled)
        notif_layout.addWidget(self.sound_check)

        self.notification_check = QCheckBox("启用桌面通知")
        self.notification_check.setChecked(self._config.notification_enabled)
        notif_layout.addWidget(self.notification_check)

        layout.addWidget(notif_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _save(self):
        config = SettingsTimerConfig(
            work_duration=self.work_spin.value(),
            short_break_duration=self.short_break_spin.value(),
            long_break_duration=self.long_break_spin.value(),
            pomodoros_until_long_break=self.pomodoros_spin.value(),
            auto_start_break=self.auto_break_check.isChecked(),
            auto_start_work=self.auto_work_check.isChecked(),
            sound_enabled=self.sound_check.isChecked(),
            notification_enabled=self.notification_check.isChecked(),
        )
        self.settings_changed.emit(config)
        self.accept()

    def get_config(self) -> SettingsTimerConfig:
        return SettingsTimerConfig(
            work_duration=self.work_spin.value(),
            short_break_duration=self.short_break_spin.value(),
            long_break_duration=self.long_break_spin.value(),
            pomodoros_until_long_break=self.pomodoros_spin.value(),
            auto_start_break=self.auto_break_check.isChecked(),
            auto_start_work=self.auto_work_check.isChecked(),
            sound_enabled=self.sound_check.isChecked(),
            notification_enabled=self.notification_check.isChecked(),
        )
