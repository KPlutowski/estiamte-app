from PyQt6.QtCore import pyqtSignal, QEvent
from PyQt6.QtWidgets import QCheckBox

from model.Item import Item


class CheckBoxItem(Item, QCheckBox):
    textEditingFinishedSignal = pyqtSignal(object)
    activeItemChangedSignal = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__()
        self.stateChanged.connect(self.text_editing_finished)

    def __repr__(self):
        return f"CheckBoxItem(name={self.objectName()})"

    def __str__(self):
        return f"CheckBoxItem(name={self.objectName()})"

    @property
    def name(self):
        return self.objectName()

    @property
    def value(self):
        if self._value == 2:
            return True
        return False

    @value.setter
    def value(self, value):
        self._value = value

    def focusInEvent(self, event: QEvent):
        super().focusInEvent(event)
        self.activeItemChangedSignal.emit(self)

    def text_editing_finished(self):
        self.textEditingFinishedSignal.emit(self)
