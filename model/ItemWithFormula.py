from enum import Enum, auto
from typing import List, Optional, Dict

from model.Enums import FormulaType
from model.Item import Item
from resources import constants

from resources.parser import Parser
from resources.utils import is_convertible_to_float


class NumberFormat(Enum):
    GENERAL = auto()
    NUMBER = auto()
    ACCOUNTING = auto()

    def format_value(self, value):
        if self == NumberFormat.GENERAL:
            return self._format_general(value)
        elif self == NumberFormat.NUMBER:
            return self._format_number(value)
        elif self == NumberFormat.ACCOUNTING:
            return self._format_accounting(value)
        else:
            return value

    @staticmethod
    def _format_general(value):
        return str(value)

    @staticmethod
    def _format_number(value):
        if is_convertible_to_float(value):
            return str(round(value, constants.DECIMAL_PLACES))
        return str(value)

    @staticmethod
    def _format_accounting(value):
        if is_convertible_to_float(value):
            if float(value) == 0:
                return f"- {constants.CURRENCY_SYMBOL}"
            else:
                return f"{round(float(value), constants.DECIMAL_PLACES)} {constants.CURRENCY_SYMBOL}"
        else:
            return str(value)


class ItemWithFormula(Item):
    def __init__(self, formula="", *args, **kwargs):
        super().__init__(formula)
        self.items_that_i_depend_on: Dict[str, ItemWithFormula] = {}  # items and their representation in formula
        self.formula_type: FormulaType = FormulaType.NO_TYPE
        self.python_formula = ''
        self.format = NumberFormat.ACCOUNTING

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    def __str__(self) -> str:
        return (
            f"{'-' * 80}\n"
            f"ItemWithFormula: {self.name}\n"
            f"self: {hex(id(self))}\n"
            f"Value: {self.value}, Formula: {self.formula}\n"
            f"Python_formula: {self.python_formula}\n"
            f"cells_that_i_dependents_on_and_names: {self.items_that_i_depend_on}\n"
            f"cells_that_dependents_on_me: {self.items_that_dependents_on_me}\n"
            f"Error Message: {self.error}, Python Formula: {self.python_formula}\n"
            f"{'-' * 80}"
        )

    @staticmethod
    def sum_function(cells: List['SpreadsheetCell']) -> float:
        """Sum the values of a list of cells."""
        total = 0.0
        for cell in cells:
            if is_convertible_to_float(cell.value):
                total += float(cell.value)
            else:
                # Handle non-numeric values if needed
                pass
        return total

    @staticmethod
    def if_function(logical_test, value_if_true, value_if_false):
        if logical_test:
            return value_if_true
        else:
            return value_if_false

    def add_dependent(self, cell: 'ItemWithFormula', reference_name: str):
        self.items_that_i_depend_on[reference_name] = cell

    def remove_dependent(self, cell: 'ItemWithFormula'):
        if cell.name in self.items_that_i_depend_on:
            del self.items_that_i_depend_on[cell.name]

    def evaluate_formula(self):
        from model.Enums import ErrorType
        from model.Model import Model
        if self.error is not None:
            pass
        try:
            if self.formula_type == FormulaType.EXPRESSION:
                self.error = None
                self.python_formula = Parser.make_python_formula(self)
                self.value = str(eval(self.python_formula))
            else:
                self.error = None
                self.value = self.formula
        except ZeroDivisionError:
            self.set_error(ErrorType.DIV)
        except ValueError:
            self.set_error(ErrorType.VALUE)
        except (SyntaxError, NameError):
            self.set_error(ErrorType.NAME)
        except Exception:
            self.set_error(ErrorType.NAME)

    def set_error(self, error: Optional['ErrorType'] = None):
        """Update the error state of this cell and propagate the change to dependent cells. """
        self.error = error
        if error is not None:
            self.value = self.error.value[0]
            self.value = self.error.value[0]

        for cell in self.items_that_dependents_on_me:
            if cell.error is not error:
                cell.set_error(error)

    def update_dependencies(self, new_dependencies: List['ItemWithFormula']):
        def remove_all_dependencies():
            for name, dep in self.items_that_i_depend_on.items():
                dep.items_that_dependents_on_me.remove(self)
            self.items_that_i_depend_on.clear()

        def add_dependencies(dependencies: List['ItemWithFormula']):
            for dep_cell in dependencies:
                if dep_cell is not None:
                    if self not in dep_cell.items_that_dependents_on_me:
                        dep_cell.items_that_dependents_on_me.append(self)

                    self.add_dependent(dep_cell, dep_cell.name)

        remove_all_dependencies()

        if self.formula.startswith('='):
            add_dependencies(new_dependencies)

    def set_item(self, formula):
        from model.Model import Model
        self.formula = formula
        self.python_formula = None
        self.set_error()
        dep = Parser.parse_formula_for_dependencies(self.formula)
        self.update_dependencies(dep)
        self.mark_dirty()
        if formula.startswith('='):
            self.formula_type = FormulaType.EXPRESSION
        elif is_convertible_to_float(formula):
            self.formula_type = FormulaType.NUMBER
        else:
            self.formula_type = FormulaType.STRING
        Model.calculate_dirty_items()

    @property
    def value(self):
        if is_convertible_to_float(self._value):
            return float(self._value)
        if self._value is '':
            return 0
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self.error:
            self._value = self.error.value[0]

        formatted_value = self.format.format_value(self._value)
        self.setText(formatted_value)
