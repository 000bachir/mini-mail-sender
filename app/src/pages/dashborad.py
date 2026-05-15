from PySide6 import QtCore
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget


class DashBorad(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Welcome to DashBorad")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            """
                color : green ; 
                font-size : 20px ; 

            """
        )
        layout.addWidget(label)
