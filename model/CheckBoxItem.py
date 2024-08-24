from PyQt6.QtWidgets import QCheckBox

from model.Item import Item


class CheckBoxItem(Item, QCheckBox):
    def __init__(self, parent):
        super().__init__()

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
