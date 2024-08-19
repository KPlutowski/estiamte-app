import re
from typing import List, Optional, Dict, Set, Union
from collections import deque, defaultdict

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget
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


class SpreadsheetCell(QTableWidgetItem):
    def __init__(self, formula="", manager=None, *args, **kwargs):
        QTableWidgetItem.__init__(self, *args, **kwargs)
        self.sheet_name = ""
        self.manager = manager
        self._value = ''
        self.formula_type: FormulaType = FormulaType.NO_TYPE
        self.error: Optional[ErrorType] = None
        self.items_that_dependents_on_me = []

        self.items_that_i_depend_on: Dict[
            str, SpreadsheetCell] = {}  # dependent items and their representation in formula
        self._formula = formula
        self.python_formula = ''

    def set_error(self, error: Optional[ErrorType] = None):
        """Update the error state of this cell and propagate the change to dependent cells. """
        if error is not None:
            # Set error
            self.error = error
            for cell in self.items_that_dependents_on_me:
                if cell.error is None:
                    cell.set_error(error)
        else:
            # Reset error
            self.error = None
            for cell in self.items_that_dependents_on_me:
                if cell.error is not None:
                    cell.set_error(None)
        self.apply_formatting_to_display_value()

    def apply_formatting_to_display_value(self):
        if self.error:
            self.value = self.error.value[0]
        self.setText(str(self.value))

    def __hash__(self):
        # Define a unique hash for each cell, e.g., based on its row and column
        return hash((self.row(), self.column()))

    def __eq__(self, other):
        # Two cells are considered equal if they have the same row and column
        if isinstance(other, SpreadsheetCell):
            return self.name == other.name
        return False

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

    def add_dependent(self, cell: 'SpreadsheetCell', reference_name: str):
        self.items_that_i_depend_on[reference_name] = cell

    def remove_dependent(self, cell: 'SpreadsheetCell'):
        if cell.name in self.items_that_i_depend_on:
            del self.items_that_i_depend_on[cell.name]

    @property
    def name(self):
        return f"{self.sheet_name}!{index_to_letter(self.column())}{self.row() + 1}"

    def update_dependencies(self, new_dependencies: List['SpreadsheetCell']):
        def remove_all_dependencies():
            for name, dep in self.items_that_i_depend_on.items():
                dep.items_that_dependents_on_me.remove(self)
            self.items_that_i_depend_on.clear()

        def add_dependencies(dependencies: List['SpreadsheetCell']):
            for dep_cell in dependencies:
                if self not in dep_cell.items_that_dependents_on_me:
                    dep_cell.items_that_dependents_on_me.append(self)
                self.add_dependent(dep_cell, dep_cell.name)

        remove_all_dependencies()

        if self.formula.startswith('='):
            add_dependencies(new_dependencies)

    def check_circular_dependency(self, target_cell: 'SpreadsheetCell') -> bool:
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

    @property
    def formula(self):
        return self._formula

    @formula.setter
    def formula(self, formula):
        self._formula = formula
        self.set_error()
        if formula.startswith('='):
            self.formula_type = FormulaType.EXPRESSION
        elif is_convertible_to_float(formula):
            self.formula_type = FormulaType.NUMBER
        else:
            self.formula_type = FormulaType.STRING

    @property
    def value(self):
        if is_convertible_to_float(self._value):
            return float(self._value)
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    # TODO
    def update_formula(self):
        # should update the cell formula after removing, moving, adding row, moving cell etc...
        # e.g. "=Sheet1!A1" after removing row A1 in Sheet1 -> "=#REF!"
        # "=Sheet1!A5"  after removing row A1 in Sheet1 -> "=Sheet1!A4"
        # "=SUM(Sheet1!A1:A10)" after removing row A1 in Sheet1 -> "=SUM(Sheet1!A1:A9)"
        # "=SUM(Sheet1!A1:A10)" after removing row A5 in Sheet1 -> "=SUM(Sheet1!A1:A9)"
        # "=SUM(Sheet1!A1:A10)" after removing row A10 in Sheet1 -> "=SUM(Sheet1!A1:A9)"
        # "=SUM(Sheet1!A1:A10)" after add row A5 in Sheet1 -> "=SUM(Sheet1!A1:A11)"
        # "=SUM(Sheet1!A1:A1)" after removing row A1 in Sheet1 -> "=SUM(#REF!)"

        # self.items_that_i_depend_on: Dict[str, SpreadsheetCell] = {}  # dependent items and their representation in formula
        if not self._formula.startswith('='):
            return
        new_formula = ""
        original_formula = self._formula
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

        self._formula = new_formula


class Spreadsheet:
    def __init__(self, table: QTableWidget, name: str, manager):
        self.table_widget = table
        self.manager = manager
        self.row_count = 0
        self.COLUMNS_COUNT = self.table_widget.columnCount()
        self.worksheet: List[List[SpreadsheetCell]] = [[SpreadsheetCell() for _ in range(self.COLUMNS_COUNT)] for _ in
                                                       range(0)]
        self.name = name

    def add_row(self, index: Optional[int] = None, text: Optional[List[str]] = None):
        if text is None:
            text = []
        if index is None:
            index = self.table_widget.rowCount()
        if index < 0 or index > self.row_count:
            raise IndexError("Index out of range")

        # Insert a new row into the worksheet and table widget
        self.worksheet.insert(index, [SpreadsheetCell(manager=self.manager) for _ in range(self.COLUMNS_COUNT)])
        self.row_count += 1
        self.table_widget.insertRow(index)

        # Set the text for each cell if provided
        for col in range(self.COLUMNS_COUNT):
            cell = self.worksheet[index][col]
            self.table_widget.setItem(index, col, cell)
            cell.sheet_name = self.name
            if col < len(text):
                cell.manager.set_cell(cell.row(), cell.column(), text[col], cell.sheet_name)
        self.reference_changed()

    def remove_row(self, index: int):
        if index < 0 or index >= self.row_count:
            return

        cells_to_remove = self.worksheet[index]

        for cell_to_remove in cells_to_remove:
            for dependent in cell_to_remove.items_that_dependents_on_me:
                dependent.remove_dependent(cell_to_remove)
                dependent.update_formula()

        for cell_to_remove in cells_to_remove:
            for name, dependent in cell_to_remove.items_that_i_depend_on.items():
                dependent.items_that_dependents_on_me.remove(cell_to_remove)

        self.worksheet.pop(index)
        self.row_count -= 1
        self.table_widget.removeRow(index)
        self.reference_changed()

    def get_cell(self, row, column):
        return self.worksheet[row][column]

    def reference_changed(self):
        for row in self.worksheet:
            for cell in row:
                cell.update_formula()


class SpreadsheetManager:
    def __init__(self):
        self._spreadsheets: Dict[str, Spreadsheet] = {}
        self._active_spreadsheet: Optional[Spreadsheet] = None
        self._dirty_cells: Set[SpreadsheetCell] = set()
        self._parser = Parser(self)
        self.current_cell: Optional[SpreadsheetCell] = None

    ###############################################################

    def add_spreadsheet(self, name: str, table_to_add: QTableWidget):
        """Add a new spreadsheet table with the given name."""
        if name in self._spreadsheets:
            raise ValueError(f"Spreadsheet with name '{name}' already exists.")
        if not isinstance(table_to_add, QTableWidget):
            raise TypeError("table_to_add must be an instance of QTableWidget.")
        self._spreadsheets[name] = Spreadsheet(table_to_add, name, self)
        self.active_spreadsheet = name

    def remove_spreadsheet(self, name: str):
        """Remove the spreadsheet table with the given name."""
        if name not in self._spreadsheets:
            raise KeyError(f"No spreadsheet found with name '{name}'.")
        # If the table to be removed is the active table, clear the active table
        if name == self._active_spreadsheet.name:
            self._active_spreadsheet = None
        del self._spreadsheets[name]

    ###############################################################

    @property
    def current_row(self) -> int:
        return self.current_cell.row()

    @property
    def current_column(self) -> int:
        return self.current_cell.column()

    ###############################################################

    @property
    def active_spreadsheet(self) -> Optional[Spreadsheet]:
        return self._active_spreadsheet

    @active_spreadsheet.setter
    def active_spreadsheet(self, name: Optional[str]):
        if name not in self._spreadsheets:
            raise KeyError(f"No spreadsheet found with name '{name}'.")
        else:
            self._active_spreadsheet = self._spreadsheets[name]
            self.current_cell = None

    ####################################################################

    def get_cell(self, row_or_address: Union[int, str], column: Optional[int] = None,
                 name_of_spreadsheet: Optional[str] = None) -> Optional[SpreadsheetCell]:
        # If column is not None, it means we're using row and column parameters
        if column is not None and name_of_spreadsheet is not None:
            if name_of_spreadsheet in self._spreadsheets:
                return self._spreadsheets[name_of_spreadsheet].get_cell(row_or_address, column)

        # If column is None, we assume we're using the address format
        elif isinstance(row_or_address, str):
            sheet_name, row_number, col_number = parse_cell_reference(row_or_address)
            if sheet_name in self._spreadsheets:
                if 0 <= row_number < self._spreadsheets[sheet_name].row_count:
                    if 0 <= col_number < self._spreadsheets[sheet_name].COLUMNS_COUNT:
                        return self._spreadsheets[sheet_name].get_cell(row_number, col_number)

        return None

    def get_range(self, start_row_or_range: Union[int, str], start_col: Optional[int] = None,
                  end_row: Optional[int] = None, end_col: Optional[int] = None,
                  sheet_name: Optional[str] = None) -> List[SpreadsheetCell]:
        # If end_row and end_col are provided, assume we're using explicit start and end coordinates
        if end_row is not None and end_col is not None and sheet_name is not None:
            return [
                self.get_cell(row, col, sheet_name)
                for row in range(start_row_or_range, end_row + 1)
                for col in range(start_col, end_col + 1)
            ]

        # If end_row and end_col are not provided, assume start_row_or_range is a range string
        elif isinstance(start_row_or_range, str):
            sheet_name, start_row, start_col, end_row, end_col = parse_cell_range(start_row_or_range)
            return [
                self.get_cell(row, col, sheet_name)
                for row in range(start_row, end_row + 1)
                for col in range(start_col, end_col + 1)
            ]

        # Return an empty list if inputs are not valid
        return []

    ####################################################################

    def set_cell(self, row, column, formula, name_of_spreadsheet=None):
        if name_of_spreadsheet is None:
            name_of_spreadsheet = self.active_spreadsheet.name
        cell_to_set = self.get_cell(row, column, name_of_spreadsheet)
        if cell_to_set is not None:
            cell_to_set.formula = formula
            new_dependencies = self._parser.parse_formula_for_dependencies(cell_to_set.formula)
            cell_to_set.update_dependencies(new_dependencies)
            self.mark_dirty(cell_to_set)
            self.calculate_spreadsheets()

    def mark_dirty(self, cell: SpreadsheetCell):
        """Mark a cell as dirty and propagate this state to its dependents."""
        if cell not in self._dirty_cells:
            self._dirty_cells.add(cell)
            to_process = deque([cell])
            processed = set()

            while to_process:
                current_cell = to_process.popleft()
                if current_cell not in processed:
                    processed.add(current_cell)
                    for dep in current_cell.items_that_dependents_on_me:
                        if dep not in self._dirty_cells:
                            self._dirty_cells.add(dep)
                        if dep not in processed:
                            to_process.append(dep)

    def calculate_spreadsheets(self):
        """Calculate and update the values of all dirty cells."""
        if not self._dirty_cells:
            return
        non_error_cells = []

        # Detect circular dependencies
        for cell in self._dirty_cells:
            for dependent in cell.items_that_dependents_on_me:
                if cell.check_circular_dependency(dependent):
                    cell.set_error(ErrorType.CIRCULAR)
            if cell.error is None:
                non_error_cells.append(cell)

        if non_error_cells:
            order = self.topological_sort(non_error_cells)
            for cell in order:
                if cell in self._dirty_cells:
                    self.evaluate_cell_formula(cell)
                    cell.apply_formatting_to_display_value()
                    self._dirty_cells.discard(cell)

        self._dirty_cells = {cell for cell in self._dirty_cells if not cell.error}
        assert not self._dirty_cells, "Some cells are still marked as dirty after calculation."

    @staticmethod
    def topological_sort(cells: List[SpreadsheetCell]) -> List[SpreadsheetCell]:
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

    ####################################################################

    def evaluate_cell_formula(self, cell: SpreadsheetCell):
        try:
            if cell.formula_type == FormulaType.EXPRESSION:
                cell.error = None
                cell.python_formula = self._parser.make_python_formula(cell)
                cell.value = str(eval(cell.python_formula))
            else:
                cell.error = None
                cell.value = cell.formula
        except ZeroDivisionError:
            cell.set_error(ErrorType.DIV)
        except ValueError:
            cell.set_error(ErrorType.VALUE)
        except (SyntaxError, NameError):
            cell.set_error(ErrorType.NAME)
        except Exception:
            cell.set_error(ErrorType.NAME)

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

    def add_row(self, index=None, text: Optional[List[str]] = None):
        self.active_spreadsheet.add_row(index, text)


class Model(QObject, SpreadsheetManager):
    def __init__(self):
        super().__init__()
