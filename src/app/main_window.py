import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTabWidget, QSplitter, QFrame, QFileDialog, QMessageBox, QMenuBar, QMenu,
    QToolBar, QStatusBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QCloseEvent
from datetime import date
from typing import Optional

from ..storage.database import Database
from ..storage.settings import SettingsManager, TimerConfig as SettingsTimerConfig
from ..timer.qt_timer import QtPomodoroTimer
from ..timer.pomodoro_timer import TimerConfig, TimerState, PomodoroPhase
from ..app.task_list import TaskListWidget
from ..app.timer_display import TimerDisplay
from ..app.search_widget import SearchWidget
from ..app.settings_dialog import SettingsDialog
from ..analytics.charts import StatsViewWidget
from ..analytics.stats_calculator import StatsCalculator
from ..analytics.csv_exporter import CSVExporter
from ..analytics.pdf_exporter import PDFExporter
from ..system.tray_icon import TrayIcon
from ..system.notifications import NotificationManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("番茄钟工作台")
        self.setMinimumSize(900, 600)

        self.db = Database()
        self.settings_manager = SettingsManager()
        self.notification_manager = NotificationManager()

        self._init_timer()
        self._init_tray()
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()
        self._load_settings()
        self._load_initial_data()

    def _init_timer(self):
        config = self.settings_manager.load_timer_config()
        timer_config = TimerConfig(
            work_duration_seconds=config.work_duration * 60,
            short_break_seconds=config.short_break_duration * 60,
            long_break_seconds=config.long_break_duration * 60,
            pomodoros_until_long_break=config.pomodoros_until_long_break,
            auto_start_break=config.auto_start_break,
            auto_start_work=config.auto_start_work,
        )
        self.timer = QtPomodoroTimer(timer_config)
        self.timer_config = config

    def _init_tray(self):
        self.tray_icon = TrayIcon()
        self.tray_icon.create()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.view_tabs = QTabWidget()
        layout.addWidget(self.view_tabs)

        self._setup_task_view()
        self._setup_stats_view()
        self._setup_split_view()

    def _setup_task_view(self):
        task_widget = QWidget()
        task_layout = QHBoxLayout(task_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        self.timer_display = TimerDisplay(self.timer, self.db)
        left_layout.addWidget(self.timer_display)

        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        self.task_list = TaskListWidget(self.db)
        right_layout.addWidget(self.task_list)

        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([300, 600])

        task_layout.addWidget(splitter)
        self.view_tabs.addTab(task_widget, "任务管理")

    def _setup_stats_view(self):
        self.stats_view = StatsViewWidget(self.db)
        self.view_tabs.addTab(self.stats_view, "统计分析")

    def _setup_split_view(self):
        split_widget = QWidget()
        split_layout = QHBoxLayout(split_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.addWidget(QLabel("<b>任务列表</b>"))
        self.split_task_list = TaskListWidget(self.db)
        left_layout.addWidget(self.split_task_list)

        middle_frame = QFrame()
        middle_layout = QVBoxLayout(middle_frame)
        middle_layout.addWidget(QLabel("<b>计时器</b>"))
        self.split_timer_display = TimerDisplay(self.timer, self.db)
        middle_layout.addWidget(self.split_timer_display)

        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(QLabel("<b>统计概览</b>"))
        self.split_stats_view = StatsViewWidget(self.db)
        right_layout.addWidget(self.split_stats_view)

        splitter.addWidget(left_frame)
        splitter.addWidget(middle_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([250, 300, 350])

        split_layout.addWidget(splitter)
        self.view_tabs.addTab(split_widget, "分屏视图")

    def _setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件(&F)")

        export_menu = file_menu.addMenu("导出")

        export_csv_action = QAction("导出CSV...", self)
        export_csv_action.triggered.connect(self._export_csv)
        export_menu.addAction(export_csv_action)

        export_pdf_action = QAction("导出PDF报告...", self)
        export_pdf_action.triggered.connect(self._export_pdf)
        export_menu.addAction(export_pdf_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("编辑(&E)")

        settings_action = QAction("设置(&S)...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._show_settings)
        edit_menu.addAction(settings_action)

        view_menu = menubar.addMenu("视图(&V)")

        task_view_action = QAction("任务管理", self)
        task_view_action.triggered.connect(lambda: self.view_tabs.setCurrentIndex(0))
        view_menu.addAction(task_view_action)

        stats_view_action = QAction("统计分析", self)
        stats_view_action.triggered.connect(lambda: self.view_tabs.setCurrentIndex(1))
        view_menu.addAction(stats_view_action)

        split_view_action = QAction("分屏视图", self)
        split_view_action.triggered.connect(lambda: self.view_tabs.setCurrentIndex(2))
        view_menu.addAction(split_view_action)

        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self):
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        start_action = QAction("开始", self)
        start_action.triggered.connect(self._start_timer)
        toolbar.addAction(start_action)

        pause_action = QAction("暂停", self)
        pause_action.triggered.connect(self._pause_timer)
        toolbar.addAction(pause_action)

        skip_action = QAction("跳过", self)
        skip_action.triggered.connect(self.timer.skip)
        toolbar.addAction(skip_action)

        toolbar.addSeparator()

        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("就绪")

    def _connect_signals(self):
        self.timer.state_changed.connect(self._on_timer_state_changed)
        self.timer.phase_changed.connect(self._on_phase_changed)
        self.timer.phase_completed.connect(self._on_phase_completed)
        self.timer.pomodoro_completed.connect(self._on_pomodoro_completed)

        self.task_list.task_selected.connect(self._on_task_selected)
        self.task_list.task_double_clicked.connect(self._on_task_double_clicked)

        self.tray_icon.show_window_requested.connect(self.show)
        self.tray_icon.quit_requested.connect(self._quit_app)
        self.tray_icon.start_requested.connect(self._start_timer)
        self.tray_icon.pause_requested.connect(self._pause_timer)
        self.tray_icon.resume_requested.connect(self._resume_timer)
        self.tray_icon.skip_requested.connect(self.timer.skip)

        self.view_tabs.currentChanged.connect(self._on_view_changed)

    def _load_settings(self):
        geometry = self.settings_manager.load_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)

        state = self.settings_manager.load_window_state()
        if state:
            self.restoreState(state)

        view_index = self.settings_manager.load_current_view()
        self.view_tabs.setCurrentIndex(view_index)

        self.notification_manager.set_sound_enabled(self.timer_config.sound_enabled)
        self.notification_manager.set_notification_enabled(self.timer_config.notification_enabled)

    def _load_initial_data(self):
        tasks = self.db.get_all_tasks()
        self.timer_display.load_tasks(tasks)
        self.split_timer_display.load_tasks(tasks)

        last_task_id = self.settings_manager.load_last_task_id()
        if last_task_id:
            self.timer_display.set_current_task(last_task_id)
            self.split_timer_display.set_current_task(last_task_id)

        self.timer_display.refresh_stats()
        self.split_timer_display.refresh_stats()

    def _start_timer(self):
        task_id = self.timer_display.get_selected_task_id() or self.task_list.get_selected_task_id()
        self.timer.start(task_id)

    def _pause_timer(self):
        self.timer.pause()

    def _resume_timer(self):
        self.timer.resume()

    def _on_timer_state_changed(self, state: TimerState):
        is_running = state == TimerState.RUNNING
        is_paused = state == TimerState.PAUSED
        self.tray_icon.update_state(is_running, is_paused)

        if state == TimerState.RUNNING:
            self.statusbar.showMessage("计时中...")
        elif state == TimerState.PAUSED:
            self.statusbar.showMessage("已暂停")
        else:
            self.statusbar.showMessage("就绪")

    def _on_phase_changed(self, phase: PomodoroPhase):
        phase_names = {
            PomodoroPhase.WORK: "工作",
            PomodoroPhase.SHORT_BREAK: "短休息",
            PomodoroPhase.LONG_BREAK: "长休息",
        }
        self.tray_icon.update_tooltip(f"番茄钟 - {phase_names[phase]}")

    def _on_phase_completed(self, phase: PomodoroPhase, start_time, end_time, is_completed):
        if phase == PomodoroPhase.WORK:
            self.notification_manager.notify_pomodoro_complete()
        elif phase == PomodoroPhase.LONG_BREAK:
            self.notification_manager.notify_long_break()
        else:
            self.notification_manager.notify_break_complete()

        self.stats_view.refresh()
        self.split_stats_view.refresh()

    def _on_pomodoro_completed(self, count: int):
        self.timer_display.refresh_stats()
        self.split_timer_display.refresh_stats()
        self.statusbar.showMessage(f"已完成 {count} 个番茄", 3000)

    def _on_task_selected(self, task_id: int):
        pass

    def _on_task_double_clicked(self, task_id: int):
        self.timer_display.set_current_task(task_id)
        self.split_timer_display.set_current_task(task_id)
        self.settings_manager.save_last_task_id(task_id)

    def _on_view_changed(self, index: int):
        self.settings_manager.save_current_view(index)

    def _show_settings(self):
        dialog = SettingsDialog(self.timer_config, self)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()

    def _apply_settings(self, config: SettingsTimerConfig):
        self.timer_config = config
        self.settings_manager.save_timer_config(config)

        timer_config = TimerConfig(
            work_duration_seconds=config.work_duration * 60,
            short_break_seconds=config.short_break_duration * 60,
            long_break_seconds=config.long_break_duration * 60,
            pomodoros_until_long_break=config.pomodoros_until_long_break,
            auto_start_break=config.auto_start_break,
            auto_start_work=config.auto_start_work,
        )
        self.timer.update_config(timer_config)

        self.notification_manager.set_sound_enabled(config.sound_enabled)
        self.notification_manager.set_notification_enabled(config.notification_enabled)

    def _export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出CSV", "", "CSV文件 (*.csv)"
        )
        if not file_path:
            return

        calculator = StatsCalculator(self.db)
        weekly = calculator.get_weekly_stats()

        if CSVExporter.export_weekly_report(weekly, file_path):
            QMessageBox.information(self, "成功", "CSV导出成功！")
        else:
            QMessageBox.warning(self, "失败", "CSV导出失败")

    def _export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出PDF报告", "", "PDF文件 (*.pdf)"
        )
        if not file_path:
            return

        calculator = StatsCalculator(self.db)
        weekly = calculator.get_weekly_stats()

        if PDFExporter.export_weekly_report(weekly, file_path):
            QMessageBox.information(self, "成功", "PDF报告导出成功！")
        else:
            QMessageBox.warning(self, "失败", "PDF报告导出失败")

    def _show_about(self):
        QMessageBox.about(
            self,
            "关于番茄钟工作台",
            "番茄钟工作台 v1.0\n\n"
            "一个基于番茄工作法的时间管理工具\n\n"
            "功能：\n"
            "• 任务管理\n"
            "• 番茄钟计时\n"
            "• 统计分析\n"
            "• 数据导出"
        )

    def _quit_app(self):
        self.settings_manager.save_window_geometry(self.saveGeometry())
        self.settings_manager.save_window_state(self.saveState())

        if self.timer.state == TimerState.RUNNING:
            reply = QMessageBox.question(
                self,
                "确认退出",
                "计时器正在运行，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self.tray_icon.hide()
        QApplication.instance().quit()

    def closeEvent(self, event: QCloseEvent):
        minimize_to_tray = self.settings_manager.load_tray_minimize()

        if minimize_to_tray and self.tray_icon:
            self.hide()
            event.ignore()
            self.tray_icon.show_message("番茄钟工作台", "程序已最小化到系统托盘")
        else:
            self.settings_manager.save_window_geometry(self.saveGeometry())
            self.settings_manager.save_window_state(self.saveState())
            event.accept()
