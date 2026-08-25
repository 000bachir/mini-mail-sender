from functools import cached_property
import sys
from PySide6 import QtCore, QtGui, QtWidgets
from typing import List


class Navbar(QtWidgets.QWidget):
    _page_changes = QtCore.Signal(int)

    def __init__(self, items: List[str], parent=None) -> None:
        super().__init__(parent)
        self.items = items
        self._setup_ui()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """Override paintEvent to draw the navbar background independently."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QtGui.QColor("#2c3e50"))

        # Draw bottom border
        pen = QtGui.QPen(QtGui.QColor("#eee"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

        painter.end()

    def _setup_ui(self):
        self.setFixedHeight(50)

        # No setStyleSheet on self — only on children
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)

        for index, label in enumerate(self.items):
            button = QtWidgets.QPushButton(label)
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 30);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 60);
                }
            """)
            button.clicked.connect(
                lambda checked, idx=index: self._page_changes.emit(idx)
            )
            layout.addWidget(button)

        layout.addStretch()
