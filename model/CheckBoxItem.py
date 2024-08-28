from PyQt6.QtCore import pyqtSignal, QEvent
from PyQt6.QtWidgets import QCheckBox

from model.Item import Item


class CheckBoxItem(Item, QCheckBox):
    textEditingFinishedSignal = pyqtSignal(object)
    activeItemChangedSignal = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__()
        self.set_item(False)
        self.stateChanged.connect(self.text_editing_finished)

    @property
    def name(self):
        return self.objectName()

    @property
    def value(self):
        if self._value is None:
            return False
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.setChecked(value)

    ###############################################

    def focusInEvent(self, event: QEvent):
        super().focusInEvent(event)
        self.activeItemChangedSignal.emit(self)

    def text_editing_finished(self):
        self.set_item(self.isChecked())
