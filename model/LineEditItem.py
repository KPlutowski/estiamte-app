from PyQt6.QtCore import QEvent, pyqtSignal
from PyQt6.QtWidgets import QLineEdit

from model.ItemWithFormula import ItemWithFormula


class LineEditItem(ItemWithFormula, QLineEdit):
    doubleClickedSignal = pyqtSignal(object)
    textEditedSignal = pyqtSignal(object, str)

    def __init__(self, formula="", *args, **kwargs):
        super().__init__(formula, *args, **kwargs)

        self.editing_text = ""
        self.editingFinished.connect(self.editing_finished)
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

    def set_display_text(self):
        self.setText(self.format.format_value(self._value))

    ###############################################

    def mouseDoubleClickEvent(self, event: QEvent):
        super().mouseDoubleClickEvent(event)
        self.doubleClickedSignal.emit(self)

    def text_edited(self, text):
        self.editing_text = text
        self.textEditedSignal.emit(self, text)

    def editing_finished(self,text=""):
        self.set_item(self.editing_text)

    def focusInEvent(self, event: QEvent):
        super().focusInEvent(event)
        self.editing_text = self.formula
        self.activeItemChangedSignal.emit(self)