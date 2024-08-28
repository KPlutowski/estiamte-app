from PyQt6.QtCore import pyqtSignal, QEvent
from PyQt6.QtWidgets import QDoubleSpinBox

from model.Item import Item


class DoubleSpinnBoxItem(Item, QDoubleSpinBox):
    textEditingFinishedSignal = pyqtSignal(object)
    activeItemChangedSignal = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__()
        self.set_item(0.0)
        self.editingFinished.connect(self.text_editing_finished)

    @property
    def value(self):
        if self._value is None:
            return 0.0
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.setValue(float(self.value))

    @property
    def name(self):
        return self.objectName()

    ###############################################

    def focusInEvent(self, event: QEvent):
        super().focusInEvent(event)
        self.activeItemChangedSignal.emit(self)

    def text_editing_finished(self):
        self.set_item(self.valueFromText(self.text()))
