from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QLineEdit

from model.ItemWithFormula import ItemWithFormula
from resources.utils import is_convertible_to_float


class LineEditItem(ItemWithFormula, QLineEdit):
    def __init__(self, formula="", *args, **kwargs):
        super().__init__(formula, *args, **kwargs)
        self.textChanged.connect(self.on_text_changed)
        self.editingFinished.connect(self.on_editing_finished)

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

    @property
    def value(self):
        if is_convertible_to_float(self._value):
            return float(self._value)
        if self._value is None:
            return 0
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self.error:
            self._value = self.error.value[0]
        self.setText(str(self.value))

    @pyqtSlot()
    def on_text_changed(self):
        print("on_text_changed")

    @pyqtSlot()
    def on_editing_finished(self):
        print("on_editing_finished")
        self.set_item(self.text())
        print(self)
