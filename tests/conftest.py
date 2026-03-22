import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for tests that need it."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()
