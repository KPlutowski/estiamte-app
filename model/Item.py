import abc
from collections import deque
from typing import Optional
from PyQt6.QtCore import pyqtSignal, QEvent

from resources.utils import is_convertible_to_float


class Item:
    textEditingFinishedSignal = pyqtSignal(object)
    activeItemChangedSignal = pyqtSignal(object)

    def __init__(self, formula=""):
        super().__init__()
        self.formula = formula
        self._value = ''
        self.error: Optional['ErrorType'] = None
        self.items_that_dependents_on_me: ['ItemWithFormula'] = []

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    @property
    def value(self):
        if is_convertible_to_float(self._value):
            return float(self._value)
        if self._value == '':
            return 0
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self.error:
            self._value = self.error.value[0]

    def mark_dirty(self):
        """Mark a cell as dirty and propagate this state to its dependents."""
        from model.Model import dirty_items

        if self not in dirty_items:
            dirty_items.add(self)
            to_process = deque([self])
            processed = set()

            while to_process:
                current_cell = to_process.popleft()
                if current_cell not in processed:
                    processed.add(current_cell)
                    for dep in current_cell.items_that_dependents_on_me:
                        if dep not in dirty_items:
                            dep.set_error()
                            dirty_items.add(dep)
                        if dep not in processed:
                            to_process.append(dep)

    def set_item(self, text):
        from model.Model import Model
        self.mark_dirty()
        self.value = text
        self.formula = text
        Model.calculate_dirty_items()

    def set_error(self, error: Optional['ErrorType'] = None):
        """Update the error state of this cell and propagate the change to dependent cells. """
        self.error = error
        if error is not None:
            self.value = self.error.value[0]

        for cell in self.items_that_dependents_on_me:
            if cell.error is not error:
                cell.set_error(error)

    def check_circular_dependency(self, target_cell: 'ItemWithFormula') -> bool:
        """Check if there is a circular dependency from target_cell to start_cell."""
        stack = [target_cell]
        visited = set()

        while stack:
            cell = stack.pop()
            if cell == self:
                return True
            if cell not in visited:
                visited.add(cell)
                stack.extend(cell.items_that_dependents_on_me)
        return False

    def focusInEvent(self, event: QEvent):
        super().focusInEvent(event)
        self.activeItemChangedSignal.emit(self)

    def editing_finished(self, text):
        pass

    def evaluate_formula(self):
        pass

    @property
    @abc.abstractmethod
    def name(self):
        pass