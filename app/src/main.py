import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QWidget,
)

main_window_style = """
    background-color : #000;
    color : #fff;
    font-size : 18px ; 

"""


class MainWindowApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Hermes")
        self.setGeometry(100, 100, 900, 700)
        self.setBaseSize(700, 700)


app = QApplication(sys.argv)

window = QWidget()
window.setStyleSheet(main_window_style)
window.show()

# start the event loop
if __name__ == "__main__":
    app.exec()
