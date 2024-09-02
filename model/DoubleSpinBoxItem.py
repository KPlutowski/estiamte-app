from PyQt6.QtWidgets import QDoubleSpinBox

from model.Item import Item


class DoubleSpinBoxItem(Item, QDoubleSpinBox):
    def __init__(self, parent):
        super().__init__()
        self.set_item(0.0)
        self.editingFinished.connect(self.editing_finished)

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

    def editing_finished(self, text=""):
        self.set_item(self.valueFromText(self.text()))
