from PyQt6.QtCore import pyqtSignal, QEvent
from PyQt6.QtWidgets import QSpinBox

from model.Item import Item


class SpinnBoxItem(Item, QSpinBox):
    textEditingFinishedSignal = pyqtSignal(object)
    activeItemChangedSignal = pyqtSignal(object)
    textEditedSignal = pyqtSignal(object, str)

    def __init__(self, parent):
        super().__init__()
        self.set_item('0')
        self.valueChanged.connect(self.text_edited)
        self.valueChanged.connect(self.text_editing_finished)

    @property
    def name(self):
        return self.objectName()

    ###############################################

    def focusInEvent(self, event: QEvent):
        super().focusInEvent(event)
        self.activeItemChangedSignal.emit(self)

    def text_editing_finished(self):
        self.textEditingFinishedSignal.emit(self)

    def text_edited(self, text):
        self.textEditedSignal.emit(self, str(text))
