from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QDialog, QLineEdit, QTextEdit, QLabel, QSpinBox,
    QMessageBox, QMenu, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from datetime import datetime
from typing import Optional, List

from ..storage.database import Database
from ..storage.models import Task, TaskStatus


class TaskEditDialog(QDialog):
    def __init__(self, task: Optional[Task] = None, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("编辑任务" if task else "新建任务")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("输入任务标题")
        if self.task:
            self.title_edit.setText(self.task.title)
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)

        layout.addWidget(QLabel("备注:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("输入任务备注（可选）")
        self.notes_edit.setMaximumHeight(100)
        if self.task:
            self.notes_edit.setPlainText(self.task.notes)
        layout.addWidget(self.notes_edit)

        pomodoro_layout = QHBoxLayout()
        pomodoro_layout.addWidget(QLabel("预估番茄数:"))
        self.estimated_spin = QSpinBox()
        self.estimated_spin.setRange(0, 100)
        self.estimated_spin.setValue(self.task.estimated_pomodoros if self.task else 0)
        pomodoro_layout.addWidget(self.estimated_spin)
        pomodoro_layout.addStretch()
        layout.addLayout(pomodoro_layout)

        if self.task:
            completed_layout = QHBoxLayout()
            completed_layout.addWidget(QLabel("已完成番茄数:"))
            self.completed_spin = QSpinBox()
            self.completed_spin.setRange(0, 100)
            self.completed_spin.setValue(self.task.completed_pomodoros)
            completed_layout.addWidget(self.completed_spin)
            completed_layout.addStretch()
            layout.addLayout(completed_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _save(self):
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入任务标题")
            return
        self.accept()

    def get_task_data(self) -> dict:
        data = {
            "title": self.title_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "estimated_pomodoros": self.estimated_spin.value(),
        }
        if self.task:
            data["completed_pomodoros"] = self.completed_spin.value()
        return data


class TaskListWidget(QWidget):
    task_selected = pyqtSignal(int)
    task_double_clicked = pyqtSignal(int)
    task_created = pyqtSignal()
    task_updated = pyqtSignal()
    task_deleted = pyqtSignal()

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._tasks: List[Task] = []
        self._highlight_text = ""
        self._setup_ui()
        self._load_tasks()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("新建任务")
        self.add_btn.clicked.connect(self._add_task)
        toolbar.addWidget(self.add_btn)

        self.archive_btn = QPushButton("查看归档")
        self.archive_btn.setCheckable(True)
        self.archive_btn.clicked.connect(self._toggle_archive_view)
        toolbar.addWidget(self.archive_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.task_list = QListWidget()
        self.task_list.itemClicked.connect(self._on_item_clicked)
        self.task_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.task_list)

    def _load_tasks(self, include_archived: bool = False):
        self._tasks = self.db.get_all_tasks(include_archived=include_archived)
        self._refresh_list()

    def _refresh_list(self):
        self.task_list.clear()
        for task in self._tasks:
            item = QListWidgetItem()
            self._update_item_text(item, task)
            item.setData(Qt.ItemDataRole.UserRole, task.id)
            self.task_list.addItem(item)

    def _update_item_text(self, item: QListWidgetItem, task: Task):
        status_icon = "✓ " if task.status == TaskStatus.ARCHIVED else ""
        text = f"{status_icon}{task.title}"
        if task.estimated_pomodoros > 0:
            text += f" [{task.completed_pomodoros}/{task.estimated_pomodoros}]"
        item.setText(text)

    def _add_task(self):
        dialog = TaskEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            task = Task(
                id=None,
                title=data["title"],
                notes=data["notes"],
                status=TaskStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                estimated_pomodoros=data["estimated_pomodoros"],
            )
            self.db.create_task(task)
            self._load_tasks(include_archived=self.archive_btn.isChecked())
            self.task_created.emit()

    def _edit_task(self, task_id: int):
        task = self.db.get_task(task_id)
        if task:
            dialog = TaskEditDialog(task, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_task_data()
                task.title = data["title"]
                task.notes = data["notes"]
                task.estimated_pomodoros = data["estimated_pomodoros"]
                if "completed_pomodoros" in data:
                    task.completed_pomodoros = data["completed_pomodoros"]
                self.db.update_task(task)
                self._load_tasks(include_archived=self.archive_btn.isChecked())
                self.task_updated.emit()

    def _archive_task(self, task_id: int):
        self.db.archive_task(task_id)
        self._load_tasks(include_archived=self.archive_btn.isChecked())

    def _delete_task(self, task_id: int):
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这个任务吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_task(task_id)
            self._load_tasks(include_archived=self.archive_btn.isChecked())
            self.task_deleted.emit()

    def _restore_task(self, task_id: int):
        task = self.db.get_task(task_id)
        if task:
            task.status = TaskStatus.ACTIVE
            self.db.update_task(task)
            self._load_tasks(include_archived=self.archive_btn.isChecked())

    def _toggle_archive_view(self):
        self._load_tasks(include_archived=self.archive_btn.isChecked())
        self.archive_btn.setText("查看活动" if self.archive_btn.isChecked() else "查看归档")

    def _on_item_clicked(self, item: QListWidgetItem):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        self.task_selected.emit(task_id)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        self.task_double_clicked.emit(task_id)

    def _show_context_menu(self, pos):
        item = self.task_list.itemAt(pos)
        if not item:
            return

        task_id = item.data(Qt.ItemDataRole.UserRole)
        task = self.db.get_task(task_id)
        if not task:
            return

        menu = QMenu(self)
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self._edit_task(task_id))
        menu.addAction(edit_action)

        if task.status == TaskStatus.ACTIVE:
            archive_action = QAction("归档", self)
            archive_action.triggered.connect(lambda: self._archive_task(task_id))
            menu.addAction(archive_action)
        else:
            restore_action = QAction("恢复", self)
            restore_action.triggered.connect(lambda: self._restore_task(task_id))
            menu.addAction(restore_action)

        menu.addSeparator()
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self._delete_task(task_id))
        menu.addAction(delete_action)

        menu.exec(self.task_list.mapToGlobal(pos))

    def search(self, query: str):
        if not query.strip():
            self._load_tasks(include_archived=self.archive_btn.isChecked())
            return
        self._tasks = self.db.search_tasks(query)
        self._highlight_text = query
        self._refresh_list_with_highlight()

    def _refresh_list_with_highlight(self):
        self.task_list.clear()
        for task in self._tasks:
            item = QListWidgetItem()
            self._update_item_text(item, task)
            item.setData(Qt.ItemDataRole.UserRole, task.id)
            self.task_list.addItem(item)

    def get_selected_task_id(self) -> Optional[int]:
        items = self.task_list.selectedItems()
        if items:
            return items[0].data(Qt.ItemDataRole.UserRole)
        return None

    def refresh(self):
        self._load_tasks(include_archived=self.archive_btn.isChecked())
