from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QGroupBox, QLabel, QSizePolicy, QWidget

from model import Item


class GroupBox(QGroupBox):
    def __init__(self, label_text="", item_name="", item_type: Item = None, index: int = 0, parent: QWidget = None):
        super().__init__(parent=parent)

        self.setTitle("")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(parent=self)
        self.horizontalLayout.addWidget(self.label)

        self.item = item_type(parent=self)
        sizePolicy = QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item.sizePolicy().hasHeightForWidth())
        self.item.setSizePolicy(sizePolicy)
        self.item.setObjectName(item_name)

        self.horizontalLayout.addWidget(self.item)

        self.label.setText(label_text)

        if parent.layout() is not None:
            parent.layout().insertWidget(index, self)

    def name(self):
        return self.item.name
