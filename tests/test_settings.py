import pytest
from PyQt6.QtCore import QSettings, QByteArray
from unittest.mock import patch, MagicMock

from src.storage.settings import SettingsManager, TimerConfig


class TestSettingsManager:
    @pytest.fixture
    def settings_manager(self):
        with patch.object(QSettings, '__init__', return_value=None):
            manager = SettingsManager()
            manager.settings = MagicMock()
            return manager

    def test_save_and_load_timer_config(self, settings_manager):
        config = TimerConfig(
            work_duration=30,
            short_break_duration=10,
            long_break_duration=20,
            pomodoros_until_long_break=3,
            auto_start_break=True,
            auto_start_work=True,
            sound_enabled=False,
            notification_enabled=False,
        )

        settings_manager.save_timer_config(config)

        settings_manager.settings.setValue.assert_called()

        settings_manager.settings.value = MagicMock(side_effect=lambda k, d=None: {
            "timer/work_duration": 30,
            "timer/short_break_duration": 10,
            "timer/long_break_duration": 20,
            "timer/pomodoros_until_long_break": 3,
            "timer/auto_start_break": True,
            "timer/auto_start_work": True,
            "timer/sound_enabled": False,
            "timer/notification_enabled": False,
        }.get(k, d))

        loaded = settings_manager.load_timer_config()

        assert loaded.work_duration == 30
        assert loaded.short_break_duration == 10
        assert loaded.long_break_duration == 20
        assert loaded.pomodoros_until_long_break == 3

    def test_save_window_geometry(self, settings_manager):
        geometry = QByteArray(b"test_geometry")
        settings_manager.save_window_geometry(geometry)

        settings_manager.settings.setValue.assert_called_with("window/geometry", geometry)

    def test_load_window_geometry(self, settings_manager):
        geometry = QByteArray(b"test_geometry")
        settings_manager.settings.value = MagicMock(return_value=geometry)

        loaded = settings_manager.load_window_geometry()

        assert loaded == geometry

    def test_save_current_view(self, settings_manager):
        settings_manager.save_current_view(2)

        settings_manager.settings.setValue.assert_called_with("window/current_view", 2)

    def test_load_current_view(self, settings_manager):
        settings_manager.settings.value = MagicMock(return_value=1)

        view = settings_manager.load_current_view()

        assert view == 1

    def test_save_recent_tasks(self, settings_manager):
        task_ids = [1, 2, 3]
        settings_manager.save_recent_tasks(task_ids)

        settings_manager.settings.setValue.assert_called()

    def test_load_recent_tasks(self, settings_manager):
        settings_manager.settings.value = MagicMock(return_value="[1, 2, 3]")

        task_ids = settings_manager.load_recent_tasks()

        assert task_ids == [1, 2, 3]

    def test_save_last_task_id(self, settings_manager):
        settings_manager.save_last_task_id(42)

        settings_manager.settings.setValue.assert_called_with("last_task_id", 42)

    def test_load_last_task_id(self, settings_manager):
        settings_manager.settings.value = MagicMock(return_value=42)

        task_id = settings_manager.load_last_task_id()

        assert task_id == 42

    def test_load_last_task_id_none(self, settings_manager):
        settings_manager.settings.value = MagicMock(return_value=-1)

        task_id = settings_manager.load_last_task_id()

        assert task_id is None

    def test_save_tray_minimize(self, settings_manager):
        settings_manager.save_tray_minimize(True)

        settings_manager.settings.setValue.assert_called_with("window/minimize_to_tray", True)

    def test_load_tray_minimize(self, settings_manager):
        settings_manager.settings.value = MagicMock(return_value=True)

        result = settings_manager.load_tray_minimize()

        assert result is True

    def test_timer_config_defaults(self):
        config = TimerConfig()

        assert config.work_duration == 25
        assert config.short_break_duration == 5
        assert config.long_break_duration == 15
        assert config.pomodoros_until_long_break == 4
        assert config.auto_start_break is False
        assert config.auto_start_work is False
        assert config.sound_enabled is True
        assert config.notification_enabled is True
