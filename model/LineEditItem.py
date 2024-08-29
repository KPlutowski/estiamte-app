from PyQt6.QtCore import QEvent, pyqtSignal
from PyQt6.QtWidgets import QLineEdit

from model.ItemWithFormula import ItemWithFormula


class LineEditItem(ItemWithFormula, QLineEdit):
    doubleClickedSignal = pyqtSignal(object)
    textEditedSignal = pyqtSignal(object,str)
    textEditingFinishedSignal = pyqtSignal(object)
    activeItemChangedSignal = pyqtSignal(object)

    def __init__(self, formula="", *args, **kwargs):
        super().__init__(formula, *args, **kwargs)
        self.editingFinished.connect(self.text_editing_finished)
        self.textEdited.connect(self.text_edited)

    def __str__(self) -> str:
        return (
            f"{'-' * 80}\n"
            f"Name: {self.name}\n"
            f"self: {hex(id(self))}\n"
            f"Value: {self.value}, Formula: {self.formula}\n"
            f"Python_formula: {self.python_formula}\n"
            f"cells_that_i_dependents_on_and_names: {self.items_that_i_depend_on}\n"
            f"cells_that_dependents_on_me: {self.items_that_dependents_on_me}\n"
            f"Error Message: {self.error}, Python Formula: {self.python_formula}\n"
            f"{'-' * 80}"
        )

    @property
    def name(self):
        return self.objectName()

    ###############################################

    def mouseDoubleClickEvent(self, event: QEvent):
        super().mouseDoubleClickEvent(event)
        self.doubleClickedSignal.emit(self)

    def focusInEvent(self, event: QEvent):
        super().focusInEvent(event)
        self.activeItemChangedSignal.emit(self)

    def text_edited(self, text):
        self.textEditedSignal.emit(self, text)

    def text_editing_finished(self):
        self.textEditingFinishedSignal.emit(self)
