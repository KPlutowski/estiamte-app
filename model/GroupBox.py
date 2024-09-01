from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QGroupBox, QLabel, QSizePolicy

from model import Item


class MovableWidget(QGroupBox):
    def __init__(self, label_text="", item_name="", item_type: Item = None, parent=None):
        super().__init__(parent=parent)

        self.setTitle("")

        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")

        self.label = QLabel(parent=self)
        self.horizontalLayout_9.addWidget(self.label)

        self.item = item_type(parent=self)
        sizePolicy = QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item.sizePolicy().hasHeightForWidth())
        self.item.setSizePolicy(sizePolicy)
        self.item.setObjectName(item_name)

        self.horizontalLayout_9.addWidget(self.item)
        parent.layout().addWidget(self)

        self.label.setText(label_text)

    def name(self):
        return self.item.name
