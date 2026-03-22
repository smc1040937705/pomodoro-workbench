import sys
from typing import Optional
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QApplication
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from pathlib import Path


class NotificationManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sound_enabled = True
        self._notification_enabled = True
        self._sound_effect: Optional[QSoundEffect] = None
        self._init_sound()

    def _init_sound(self):
        self._sound_effect = QSoundEffect()
        self._sound_effect.setVolume(0.5)

    def set_sound_enabled(self, enabled: bool):
        self._sound_enabled = enabled

    def set_notification_enabled(self, enabled: bool):
        self._notification_enabled = enabled

    def notify_pomodoro_complete(self):
        message = "番茄时间结束！休息一下吧。"
        self._send_notification("番茄完成", message)
        self._play_sound()

    def notify_break_complete(self):
        message = "休息结束，准备开始新的番茄时间！"
        self._send_notification("休息结束", message)
        self._play_sound()

    def notify_long_break(self):
        message = "恭喜完成一组番茄！享受长休息时间。"
        self._send_notification("长休息", message)
        self._play_sound()

    def _send_notification(self, title: str, message: str):
        if not self._notification_enabled:
            return

        if sys.platform == "win32":
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5, threaded=True)
            except ImportError:
                self._fallback_notification(title, message)
        elif sys.platform == "darwin":
            import subprocess
            subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'])
        else:
            self._fallback_notification(title, message)

    def _fallback_notification(self, title: str, message: str):
        app = QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if hasattr(widget, "tray_icon") and widget.tray_icon:
                    widget.tray_icon.show_message(title, message)
                    break

    def _play_sound(self):
        if not self._sound_enabled or not self._sound_effect:
            return

        sound_file = Path(__file__).parent / "sounds" / "notification.wav"
        if sound_file.exists():
            self._sound_effect.setSource(QUrl.fromLocalFile(str(sound_file)))
            self._sound_effect.play()
        else:
            if sys.platform == "win32":
                import winsound
                winsound.Beep(1000, 500)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
            else:
                print("\a")

    def play_custom_sound(self, sound_path: str):
        if not self._sound_enabled or not self._sound_effect:
            return

        self._sound_effect.setSource(QUrl.fromLocalFile(sound_path))
        self._sound_effect.play()
