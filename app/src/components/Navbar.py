from functools import cached_property
import sys
from PySide6 import QtCore, QtGui, QtWidgets


class Page(QtWidgets.QWidget):
    complete_changes = QtCore.SIGNAL()
