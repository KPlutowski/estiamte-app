from typing import List, Optional, Dict

from model.Enums import FormulaType
from model.Item import Item

from resources.parser import Parser
from resources.utils import is_convertible_to_float


class ItemWithFormula(Item):
    def __init__(self, formula="", *args, **kwargs):
        super().__init__(formula)
        self.items_that_i_depend_on: Dict[str, ItemWithFormula] = {}  # items and their representation in formula
        self.formula_type: FormulaType = FormulaType.NO_TYPE
        self.python_formula = ''

    def __hash__(self):
        # Define a unique hash for each cell, e.g., based on its row and column
        return hash(self.name)

    def __eq__(self, other):
        # Two cells are considered equal if they have the same row and column
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
