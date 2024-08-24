from PyQt6.QtWidgets import QSpinBox

from model.Item import Item


class SpinnBoxItem(Item, QSpinBox):
    def __init__(self, parent):
        super().__init__()

    def __repr__(self):
        return f"SpinnBoxItem(name={self.objectName()})"

    def __str__(self):
        return f"SpinnBoxItem(name={self.objectName()})"

    @property
    def name(self):
        return self.objectName()
