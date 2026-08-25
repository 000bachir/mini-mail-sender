import sys
from PySide6 import QtGui
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QFrame,
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, Property, QRect
from PySide6.QtGui import QFont, QIcon, QColor, QPainter, QPen, QBrush, QLinearGradient


# ── Palette ────────────────────────────────────────────────────────────────────
BG_DARK = "#0d0f14"
SIDEBAR_BG = "#12151c"
ACCENT = "#4f8ef7"
ACCENT_GLOW = "#1e3a6e"
TEXT_PRIMARY = "#e8eaf0"
TEXT_MUTED = "#5a6070"
HOVER_BG = "#1c2030"
ACTIVE_BG = "#1a2540"
BORDER = "#1e2333"


PAGES = [
    ("dashboard", "⊞", "Dashboard"),
    ("compose", "✉", "Compose"),
    ("contacts", "◎", "Contacts"),
    ("scheduled", "◷", "Scheduled"),
    ("sent", "✓", "Sent Log"),
    ("settings", "⚙", "Settings"),
]


class SideBarButton(QPushButton):
    def __init__(self, icon_char: str, label: str, page_key: str, parent=None) -> None:
        super().__init__(parent)
        self.page_key = page_key
        self.icon_char = icon_char
        self.label = label
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
