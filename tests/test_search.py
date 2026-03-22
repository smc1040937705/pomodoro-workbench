import pytest
from src.app.search_widget import SearchWidget


class TestSearchHighlight:
    def test_highlight_text_basic(self):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "Python")
        assert result == "【Python】开发任务"

    def test_highlight_text_case_insensitive(self):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "python")
        assert "python" in result.lower()

    def test_highlight_text_multiple_matches(self):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发Python测试", "Python")
        assert result.count("【Python】") == 2

    def test_highlight_text_no_match(self):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "Java")
        assert result == "Python开发任务"

    def test_highlight_text_empty_query(self):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "")
        assert result == "Python开发任务"

    def test_highlight_text_partial_match(self):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "Py")
        assert result == "【Py】thon开发任务"

    def test_highlight_text_chinese(self):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("Python开发任务", "开发")
        assert result == "Python【开发】任务"

    def test_highlight_text_special_chars(self):
        widget = SearchWidget(None)
        result = widget.get_highlighted_text("任务(重要)", "(")
        assert result == "任务【(】重要)"
