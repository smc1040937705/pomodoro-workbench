import pytest
from PyQt6.QtWidgets import QApplication
from src.app.search_widget import SearchWidget


@pytest.fixture(scope="module")
def qapp():
    """确保 QApplication 实例存在"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestSearchHighlight:
    def test_highlight_text_basic(self, qapp):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "Python")
        assert result == "【Python】开发任务"

    def test_highlight_text_case_insensitive(self, qapp):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "python")
        assert "python" in result.lower()

    def test_highlight_text_multiple_matches(self, qapp):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发Python测试", "Python")
        assert result.count("【Python】") == 2

    def test_highlight_text_no_match(self, qapp):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "Java")
        assert result == "Python开发任务"

    def test_highlight_text_empty_query(self, qapp):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "")
        assert result == "Python开发任务"

    def test_highlight_text_partial_match(self, qapp):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "Py")
        assert result == "【Py】thon开发任务"

    def test_highlight_text_chinese(self, qapp):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "开发")
        assert result == "Python【开发】任务"

    def test_highlight_text_special_chars(self, qapp):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("任务(重要)", "(")
        assert result == "任务【(】重要)"
