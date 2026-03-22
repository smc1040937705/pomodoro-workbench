from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCharFormat, QTextDocument, QBrush, QColor
from typing import List
import re

from ..storage.database import Database
from ..storage.models import Task


class SearchWidget(QWidget):
    task_selected = pyqtSignal(int)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._results: List[Task] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索任务标题或备注...")
        self.search_input.textChanged.connect(self._on_search)
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        self.clear_btn = QPushButton("清除")
        self.clear_btn.clicked.connect(self._clear_search)
        search_layout.addWidget(self.clear_btn)

        layout.addLayout(search_layout)

        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self._on_item_clicked)
        self.result_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.result_list)

        self.result_label = QLabel("输入关键词开始搜索")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_label)

    def _on_search(self):
        query = self.search_input.text().strip()
        if not query:
            self._results = []
            self.result_list.clear()
            self.result_label.setText("输入关键词开始搜索")
            return

        self._results = self.db.search_tasks(query)
        self._refresh_results(query)

    def _refresh_results(self, query: str):
        self.result_list.clear()
        for task in self._results:
            item = QListWidgetItem()
            highlighted_title = self._highlight_text(task.title, query)
            item.setText(highlighted_title)
            item.setData(Qt.ItemDataRole.UserRole, task.id)
            if task.notes:
                item.setToolTip(task.notes)
            self.result_list.addItem(item)

        self.result_label.setText(f"找到 {len(self._results)} 个结果")

    def _highlight_text(self, text: str, query: str) -> str:
        if not query:
            return text

        pattern = re.compile(re.escape(query), re.IGNORECASE)
        result = []
        last_end = 0

        for match in pattern.finditer(text):
            result.append(text[last_end:match.start()])
            result.append(f"【{match.group()}】")
            last_end = match.end()

        result.append(text[last_end:])
        return "".join(result)

    def _clear_search(self):
        self.search_input.clear()
        self._results = []
        self.result_list.clear()
        self.result_label.setText("输入关键词开始搜索")

    def _on_item_clicked(self, item: QListWidgetItem):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        self.task_selected.emit(task_id)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        self.task_selected.emit(task_id)

    def get_highlighted_text(self, text: str, query: str) -> str:
        return self._highlight_text(text, query)
