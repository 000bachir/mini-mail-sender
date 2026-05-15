from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel, QVBoxLayout


class Setting(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        label = QLabel("Settings page")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(label)
