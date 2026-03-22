import sys
from typing import Optional, Callable
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal


class TrayIcon(QObject):
    show_window_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    start_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    resume_requested = pyqtSignal()
    skip_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tray_icon: Optional[QSystemTrayIcon] = None
        self._menu: Optional[QMenu] = None
        self._is_running = False
        self._is_paused = False

    def create(self, icon_path: Optional[str] = None):
        if sys.platform == "win32":
            icon = QIcon.fromTheme("applications-clock")
            if icon.isNull():
                from PyQt6.QtGui import QPixmap, QPainter, QColor
                pixmap = QPixmap(64, 64)
                pixmap.fill(QColor(0, 0, 0, 0))
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setBrush(QColor("#e74c3c"))
                painter.drawEllipse(4, 4, 56, 56)
                painter.setBrush(QColor("#ffffff"))
                painter.drawRect(30, 12, 4, 20)
                painter.drawRect(30, 30, 16, 4)
                painter.end()
                icon = QIcon(pixmap)
        else:
            icon = QIcon.fromTheme("timer")

        self._tray_icon = QSystemTrayIcon(icon)
        self._tray_icon.setToolTip("番茄钟工作台")

        self._create_menu()
        self._tray_icon.setContextMenu(self._menu)
        self._tray_icon.activated.connect(self._on_activated)
        self._tray_icon.show()

    def _create_menu(self):
        self._menu = QMenu()

        self._show_action = QAction("显示窗口", self)
        self._show_action.triggered.connect(self.show_window_requested)
        self._menu.addAction(self._show_action)

        self._menu.addSeparator()

        self._start_action = QAction("开始", self)
        self._start_action.triggered.connect(self.start_requested)
        self._menu.addAction(self._start_action)

        self._pause_action = QAction("暂停", self)
        self._pause_action.triggered.connect(self.pause_requested)
        self._pause_action.setVisible(False)
        self._menu.addAction(self._pause_action)

        self._resume_action = QAction("继续", self)
        self._resume_action.triggered.connect(self.resume_requested)
        self._resume_action.setVisible(False)
        self._menu.addAction(self._resume_action)

        self._skip_action = QAction("跳过", self)
        self._skip_action.triggered.connect(self.skip_requested)
        self._menu.addAction(self._skip_action)

        self._menu.addSeparator()

        self._quit_action = QAction("退出", self)
        self._quit_action.triggered.connect(self.quit_requested)
        self._menu.addAction(self._quit_action)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window_requested.emit()

    def update_state(self, is_running: bool, is_paused: bool = False):
        self._is_running = is_running
        self._is_paused = is_paused

        self._start_action.setVisible(not is_running)
        self._pause_action.setVisible(is_running and not is_paused)
        self._resume_action.setVisible(is_paused)

    def update_tooltip(self, text: str):
        if self._tray_icon:
            self._tray_icon.setToolTip(text)

    def show_message(self, title: str, message: str, duration: int = 3000):
        if self._tray_icon:
            self._tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, duration)

    def hide(self):
        if self._tray_icon:
            self._tray_icon.hide()

    def show(self):
        if self._tray_icon:
            self._tray_icon.show()
