import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("番茄钟工作台")
    app.setOrganizationName("PomodoroWorkbench")

    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
