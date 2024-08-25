from PyQt6.QtCore import pyqtSignal, QEvent
from PyQt6.QtWidgets import QDoubleSpinBox

from model.Item import Item


class DoubleSpinnBoxItem(Item, QDoubleSpinBox):
    textEditingFinishedSignal = pyqtSignal(object)
    activeItemChangedSignal = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__()
        self.editingFinished.connect(self.text_editing_finished)

    def __repr__(self):
        return f"DoubleSpinnBoxItem(name={self.objectName()})"

    def __str__(self):
        return f"DoubleSpinnBoxItem(name={self.objectName()})"

    @property
    def name(self):
        return self.objectName()

    ###############################################

    def focusInEvent(self, event: QEvent):
        super().focusInEvent(event)
        self.activeItemChangedSignal.emit(self)

    def text_editing_finished(self):
        self.textEditingFinishedSignal.emit(self)


