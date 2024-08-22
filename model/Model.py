from typing import List, Optional, Dict, Set, Union
from collections import deque, defaultdict

from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget, QWidget, QSpinBox
from enum import Enum
from resources.utils import *
from resources.parser import Parser, Tokenizer, ValueType, TokenType


class ErrorType(Enum):
    REF = ("#REF!", 'Invalid cell reference.')
    DIV = ('#DIV/0!', 'Division by zero.')
    NAME = ('#NAME?', 'Invalid function or range name.')
    VALUE = ('#VALUE!', 'Wrong type of argument or operand.')
    NA = ('#N/A', 'A value is not available.')
    NUM = ('#NUM!', 'Invalid numeric value.')
    NULL = ('#NULL!', 'Incorrect use of range in formula.')
    CIRCULAR = ('#CIRCULAR!', 'Circular reference detected.')


class FormulaType(Enum):
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    EXPRESSION = 'EXPRESSION'
    NO_TYPE = 'NO_TYPE'


class Item:
    def __init__(self):
        super().__init__()
        self._value = ''
        self.error: Optional[ErrorType] = None
        self.items_that_dependents_on_me: ['ItemWithFormula'] = []

    @property
    def value(self):
        if is_convertible_to_float(self._value):
            return float(self._value)
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def name(self):
        return ""

    def __str__(self) -> str:
        return (
            f"{'-' * 80}\n"
            f"Item: {self.name}\n"
            f"self: {hex(id(self))}\n"
            f"cells_that_dependents_on_me: {self.items_that_dependents_on_me}\n"
            f"{'-' * 80}"
        )

    def mark_dirty(self):
        """Mark a cell as dirty and propagate this state to its dependents."""
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
                            dirty_items.add(dep)
                        if dep not in processed:
                            to_process.append(dep)

    def set_item(self, text):
        self.mark_dirty()
        self.value = text
        Model.calculate_dirty_items()

    def set_error(self, error: Optional[ErrorType] = None):
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

    def evaluate_formula(self):
        pass


class ItemWithFormula(Item):
    def __init__(self, formula="", *args, **kwargs):
        super().__init__()
        self.items_that_i_depend_on: Dict[str, ItemWithFormula] = {}  # items and their representation in formula
        self.formula_type: FormulaType = FormulaType.NO_TYPE
        self.formula = formula
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
        try:
            if self.formula_type == FormulaType.EXPRESSION:
                self.error = None
                self.python_formula = Parser.make_python_formula(self)
                self.set_value(str(eval(self.python_formula)))
            else:
                self.error = None
                self.set_value(self.formula)
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
        self.formula = formula
        self.set_error()
        self.mark_dirty()
        if formula.startswith('='):
            self.formula_type = FormulaType.EXPRESSION
            dep = Parser.parse_formula_for_dependencies(self.formula)
            self.update_dependencies(dep)
        elif is_convertible_to_float(formula):
            self.formula_type = FormulaType.NUMBER
        else:
            self.formula_type = FormulaType.STRING
        Model.calculate_dirty_items()

    def set_value(self, value):
        self._value = value
        if self.error:
            self._value = self.error.value[0]


class SpreadsheetCell(ItemWithFormula, QTableWidgetItem):
    def __init__(self, formula="", *args, **kwargs):
        super().__init__(formula, *args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{'-' * 80}\n"
            f"Cell at: row = {self.row()}, column = {self.column()}, Name: {self.name}\n"
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
        return f"{self.tableWidget().objectName()}!{index_to_letter(self.column())}{self.row() + 1}"

    def set_value(self, value):
        self._value = value
        if self.error:
            self._value = self.error.value[0]
        self.setText(str(self.value))

    # TODO
    def update_formula_after_moving(self):
        # should update the cell formula after removing, moving, adding row, moving cell etc...
        # e.g. "=Sheet1!A1" after removing row A1 in Sheet1 -> "=#REF!"
        # "=Sheet1!A5"  after removing row A1 in Sheet1 -> "=Sheet1!A4"
        # "=SUM(Sheet1!A1:A10)" after removing row A1 in Sheet1 -> "=SUM(Sheet1!A1:A9)"
        # "=SUM(Sheet1!A1:A10)" after removing row A5 in Sheet1 -> "=SUM(Sheet1!A1:A9)"
        # "=SUM(Sheet1!A1:A10)" after removing row A10 in Sheet1 -> "=SUM(Sheet1!A1:A9)"
        # "=SUM(Sheet1!A1:A10)" after add row A5 in Sheet1 -> "=SUM(Sheet1!A1:A11)"
        # "=SUM(Sheet1!A1:A1)" after removing row A1 in Sheet1 -> "=SUM(#REF!)"

        # self.items_that_i_depend_on: Dict[str, SpreadsheetCell] = {}  # dependent items and their representation in formula
        if not self.formula.startswith('='):
            return
        new_formula = ""
        original_formula = self.formula
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(original_formula)

        def adjust_cell_reference(cell_ref: str) -> str:
            # cell_ref eg "Sheet1!A5"
            if cell_ref not in self.items_that_i_depend_on:
                return f'#REF!'
            return self.items_that_i_depend_on.get(cell_ref).name

            # sheet_name_old, row_index_old, col_index_old = parse_cell_reference(cell_ref)
            # for dependent in self.items_that_i_depend_on.values():
            #     if cell_ref in dependent.items_that_i_depend_on:
            #         pass
            # adjusted_cell_ref = f"{sheet_name}!{index_to_letter(new_col)}{new_row + 1}"

        # TODO
        def adjust_cell_range_reference(cell_ref: str):
            return cell_ref

        for token in tokens:
            if token.token_type == TokenType.VALUE and token.subtype == ValueType.IDENTIFIER:
                if is_valid_cell_reference(token.value):
                    acr = adjust_cell_reference(token.value)
                    if acr == "#REF!":
                        self.set_error(ErrorType.REF)
                    new_formula += acr
                elif is_valid_cell_range(token.value):
                    new_formula += adjust_cell_range_reference(token.value)
                else:
                    new_formula += token.value
            else:
                # For other token types (operators, functions, etc.)
                new_formula += token.value

        self.formula = new_formula


class SpinnBoxCell(Item, QSpinBox):
    def __init__(self, parent):
        super().__init__()

    def __repr__(self):
        return f"SpinnBoxCell(name={self.objectName()})"

    def __str__(self):
        return f"SpinnBoxCell(name={self.objectName()})"

    @property
    def name(self):
        return self.objectName()


class Spreadsheet(QTableWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        self.worksheet: List[List[SpreadsheetCell]] = [[SpreadsheetCell() for _ in range(self.columnCount())] for _ in
                                                       range(0)]

    def add_row(self, index: Optional[int] = None, text: Optional[List[str]] = None):
        if text is None:
            text = []
        if index is None:
            index = self.rowCount()
        if index < 0 or index > self.rowCount():
            raise IndexError("Index out of range")

        self.worksheet.insert(index, [SpreadsheetCell() for _ in range(self.columnCount())])
        self.insertRow(index)

        for col in range(self.columnCount()):
            cell = self.worksheet[index][col]
            self.setItem(index, col, cell)
            cell.sheet_name = self.objectName()

        for col in range(self.columnCount()):
            if col < len(text):
                cell = self.worksheet[index][col]
                cell.set_item(text[col])
        self.reference_changed()

    def remove_row(self, index: int):
        if index < 0 or index >= self.rowCount():
            return

        cells_to_remove = self.worksheet[index]

        for cell_to_remove in cells_to_remove:
            for dependent in cell_to_remove.items_that_dependents_on_me:
                dependent.remove_dependent(cell_to_remove)
                dependent.update_formula_after_moving()

        for cell_to_remove in cells_to_remove:
            for name, dependent in cell_to_remove.items_that_i_depend_on.items():
                dependent.items_that_dependents_on_me.remove(cell_to_remove)

        self.worksheet.pop(index)
        self.removeRow(index)
        self.reference_changed()

    def get_cell(self, row, column):
        if 0 <= row < self.rowCount() and 0 <= column < self.columnCount():
            return self.worksheet[row][column]
        return None

    def reference_changed(self):
        for row in self.worksheet:
            for cell in row:
                cell.update_formula_after_moving()


class Model:
    __active_item = None

    @staticmethod
    def set_active_spreadsheet(name):
        Model.__active_item = None
        if name in db:
            if isinstance(db[name], Spreadsheet):
                Model.__active_item = db[name]

    @staticmethod
    def get_active_spreadsheet() -> Spreadsheet:
        return Model.__active_item

    @staticmethod
    def add_item(widget: QWidget):
        if widget.objectName() not in db:
            name = widget.objectName()
            db[name] = widget
        else:
            raise NameError(f'!!ERROR AT Model.add_item, name:{widget.objectName()}!!')

    @staticmethod
    def calculate_dirty_items():
        """Calculate and update the values of all dirty cells."""
        global dirty_items

        def topological_sort(cells: List[Item]) -> List[Item]:
            """Perform a topological sort of the cells based on their dependencies, excluding cells with errors."""
            # Filter out cells with errors
            cells = [cell for cell in cells if cell.error is None]

            if not cells:
                return []

            # Initialize in-degree count for each cell
            in_degree = defaultdict(int)
            for cell in cells:
                for dependent in cell.items_that_dependents_on_me:
                    if dependent in cells:
                        in_degree[dependent] += 1

            # Initialize queue with cells that have zero in-degree
            zero_in_degree = deque(cell for cell in cells if in_degree[cell] == 0)
            topological_order = []

            while zero_in_degree:
                cell = zero_in_degree.popleft()
                topological_order.append(cell)
                for dependent in cell.items_that_dependents_on_me:
                    if dependent in cells:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            zero_in_degree.append(dependent)

            if len(topological_order) != len(cells):
                raise RuntimeError("Cyclic dependency detected")
            return topological_order

        if not dirty_items:
            return
        non_error_cells = []

        # Detect circular dependencies
        for cell in dirty_items:
            for dependent in cell.items_that_dependents_on_me:
                if cell.check_circular_dependency(dependent):
                    cell.set_error(ErrorType.CIRCULAR)
            if cell.error is None:
                non_error_cells.append(cell)

        if non_error_cells:
            order = topological_sort(non_error_cells)
            for cell in order:
                if cell in dirty_items:
                    cell.evaluate_formula()
                    dirty_items.discard(cell)

        dirty_items = {cell for cell in dirty_items if not cell.error}
        assert not dirty_items, "Some cells are still marked as dirty after calculation."

    @staticmethod
    def remove_spreadsheet(name: str):
        """Remove the spreadsheet table with the given name."""
        if name not in db:
            raise KeyError(f"No spreadsheet found with name '{name}'.")
        del db[name]

    @staticmethod
    def add_row(index=None, text: Optional[List[str]] = None, name=None):
        if name in db:
            db[name].add_row(index, text)

    @staticmethod
    def remove_row(index=None, name=None):
        if name in db:
            db[name].remove_row(index)

    @staticmethod
    def get_cell(row_or_address: Union[int, str], column: Optional[int] = None,
                 name_of_spreadsheet: Optional[str] = None) -> Optional[SpreadsheetCell]:
        # If column is not None, it means we're using row and column parameters
        if column is not None and name_of_spreadsheet is not None:
            if name_of_spreadsheet in db:
                return db[name_of_spreadsheet].get_cell(row_or_address, column)

        # If column is None, we assume we're using the address format
        elif isinstance(row_or_address, str):
            sheet_name, row_number, col_number = parse_cell_reference(row_or_address)
            if sheet_name in db:
                if 0 <= row_number < db[sheet_name].rowCount():
                    if 0 <= col_number < db[sheet_name].columnCount():
                        return db[sheet_name].get_cell(row_number, col_number)
        return None

    @staticmethod
    def get_range(start_row_or_range: Union[int, str], start_col: Optional[int] = None,
                  end_row: Optional[int] = None, end_col: Optional[int] = None, sheet_name: Optional[str] = None) -> List[SpreadsheetCell]:
        # If end_row and end_col are provided, assume we're using explicit start and end coordinates
        if end_row is not None and end_col is not None and sheet_name is not None:
            return [
                Model.get_cell(row, col, sheet_name)
                for row in range(start_row_or_range, end_row + 1)
                for col in range(start_col, end_col + 1)
            ]

        # If end_row and end_col are not provided, assume start_row_or_range is a range string
        elif isinstance(start_row_or_range, str):
            sheet_name, start_row, start_col, end_row, end_col = parse_cell_range(start_row_or_range)
            return [
                Model.get_cell(row, col, sheet_name)
                for row in range(start_row, end_row + 1)
                for col in range(start_col, end_col + 1)
            ]

        # Return an empty list if inputs are not valid
        return []

    @staticmethod
    def get_property(address: str):
        name = address[len('PROPERTIES!'):]
        if not name:
            return None
        return db.get(name)


dirty_items: Set[Item] = set()
db: Dict[str, any] = {}


