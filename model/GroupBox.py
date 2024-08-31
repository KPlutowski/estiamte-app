from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QGroupBox, QLabel, QHBoxLayout, QSizePolicy

from model import Item


class MovableWidget(QGroupBox):
    def __init__(self, r, label_text="", item_name="", item_type: Item = None, parent=None):
        super().__init__(parent=parent)

        self.setTitle("")

        self.label = QLabel(parent=self)
        self.item = item_type(parent=self)

        self.label.setText(label_text)

        sizePolicy = QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item.sizePolicy().hasHeightForWidth())
        self.item.setSizePolicy(sizePolicy)
        self.item.setObjectName(item_name)

        # Store row
        self.r = r

        # layout
        tmphorizontalLayout = QHBoxLayout(self)
        tmphorizontalLayout.setContentsMargins(0, 0, 0, 0)

        tmphorizontalLayout.addWidget(self.label)
        tmphorizontalLayout.addWidget(self.item)

    def relabel(self, r):
        """Set button label text given row/col"""
        self.label.setText(f"Current Row: {r}")
