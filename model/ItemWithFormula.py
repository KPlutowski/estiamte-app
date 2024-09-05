import abc
from enum import Enum, auto
from typing import List, Dict

from model.Enums import FormulaType, ErrorType
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
                return f" - {constants.CURRENCY_SYMBOL}"
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
        self.format = NumberFormat.GENERAL

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

    def add_dependent(self, cell: 'ItemWithFormula', reference_name: str):
        self.items_that_i_depend_on[reference_name] = cell

    def remove_dependent(self, cell: 'ItemWithFormula'):
        if cell.name in self.items_that_i_depend_on:
            self.formula = self.formula.replace(cell.name,ErrorType.REF.value[0])
            self.set_error(ErrorType.REF)
            del self.items_that_i_depend_on[cell.name]

    def evaluate_formula(self):
        from model.Enums import ErrorType
        from model.Model import Model

        if self.error is not None:
            pass
        self.error = None
        try:
            if self.formula_type == FormulaType.EXPRESSION:
                self.python_formula = Parser.make_python_formula(self.formula)
                self.value = Model.evaluate_formula(self.python_formula)
            else:
                self.value = self.formula
        except ZeroDivisionError:
            self.set_error(ErrorType.DIV)
        except ValueError:
            self.set_error(ErrorType.VALUE)
        except (SyntaxError, NameError):
            self.set_error(ErrorType.NAME)
        except Exception:
            self.set_error(ErrorType.NAME)

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
        self.mark_dirty()
        self.formula = formula
        self.python_formula = None
        self.set_error()
        dep = Parser.parse_formula_for_dependencies(self.formula)
        self.update_dependencies(dep)
        self.formula_type = FormulaType.determine_formula_type(formula)
        Model.calculate_dirty_items()

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
        self.set_display_text()

    @abc.abstractmethod
    def set_display_text(self):
        pass

    def clean_up(self):
        for item in self.items_that_dependents_on_me:
            item.remove_dependent(self)
        for name,item in self.items_that_i_depend_on.items():
            item.items_that_i_depend_on.pop(self.name)

        self.items_that_dependents_on_me.clear()
        self.items_that_i_depend_on.clear()

