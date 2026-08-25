from PySide6 import QtCore
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget


class Email_Managers(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel(
            "Welcome to Email Manager in this section , you can store in emails found in the database "
        )
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            """
                color : green ; 
                font-size : 20px ; 

            """
        )
        layout.addWidget(label)
