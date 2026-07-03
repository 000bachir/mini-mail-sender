import signal
import sys
import time
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout

from app.src.components.Navbar import Navbar
from app.src.pages.dashborad import DashBorad
from app.src.pages.settings import Setting
from app.src.pages.Contacts_Manager import Email_Managers


class MainEntyPoint(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hermes")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("""
            background-color : #181818;
        """)
        self._setup_ui()

    def _setup_ui(self):
        central = QtWidgets.QWidget()

        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # importing and setting the navbar component :
        self.navbar = Navbar(["Dashborad", "Settings", "Emails"])
        layout.addWidget(self.navbar)

        # setting the pages :
        self.pages = QStackedWidget()
        self.pages.addWidget(DashBorad())
        self.pages.addWidget(Setting())
        self.pages.addWidget(Email_Managers())

        layout.addWidget(self.pages)

        self.navbar._page_changes.connect(self.pages.setCurrentIndex)


def main():
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    timer = QtCore.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    window = MainEntyPoint()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
