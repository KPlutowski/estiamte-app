from PyQt6.QtWidgets import QDoubleSpinBox

from model.Item import Item


class DoubleSpinnBoxItem(Item, QDoubleSpinBox):
    def __init__(self, parent):
        super().__init__()

    def __repr__(self):
        return f"DoubleSpinnBoxItem(name={self.objectName()})"

    def __str__(self):
        return f"DoubleSpinnBoxItem(name={self.objectName()})"

    @property
    def name(self):
        return self.objectName()
