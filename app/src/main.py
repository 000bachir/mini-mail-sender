import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout

from app.src.components.Navbar import Navbar
from app.src.pages.dashborad import DashBorad
from app.src.pages.settings import Setting


class MainEntyPoint(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hermes")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("""
            background-color : #000;
        """)
        self._setup_ui()

    def _setup_ui(self):
        central = QtWidgets.QWidget()

        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # importing and setting the navbar component :
        self.navbar = Navbar(["Dashborad", "Settings", "About", "Contact"])
        layout.addWidget(self.navbar)

        # setting the pages :
        self.pages = QStackedWidget()
        self.pages.addWidget(DashBorad())
        self.pages.addWidget(Setting())

        layout.addWidget(self.pages)

        self.navbar._page_changes.connect(self.pages.setCurrentIndex)


def main():
    app = QApplication(sys.argv)
    window = MainEntyPoint()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
