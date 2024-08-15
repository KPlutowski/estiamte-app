import re
from typing import List, Optional, Dict, Set
from collections import deque, defaultdict
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget
from enum import Enum
from utilities import *
from parser import Parser


class ErrorType(Enum):
    REF = ("#REF!", 'Invalid cell reference.')
    DIV = ('#DIV/0!', 'Division by zero.')
    NAME = ('#NAME?', 'Invalid function or range name.')
    VALUE = ('#VALUE!', 'Wrong type of argument or operand.')
    NA = ('#N/A', 'A value is not available.')
    NUM = ('#NUM!', 'Invalid numeric value.')
    NULL = ('#NULL!', 'Incorrect use of range in formula.')
    CIRCULAR = ('#CIRCULAR!', 'Circular reference detected.')


class SpreadsheetCell(QTableWidgetItem):
    def __init__(self,*args, **kwargs):
        QTableWidgetItem.__init__(self, *args, **kwargs)
        self.spreadsheet_name = ""
        self.value = ''
        self.error: Optional[ErrorType] = None
        self.items_that_dependents_on_me = []

        self.items_that_i_depend_on: Dict[str, SpreadsheetCell] = {}  # dependent items and their representation in formula
        self.formula = ''
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
        self.setText(self.value)

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
        if self.formula.find(cell.name) != -1:
            range_pattern_ref_1 = re.compile(r'([A-Za-z_\u00C0-\u017F][A-Za-z0-9_\u00C0-\u017F]*)!([A-Z]+)(\d+):(#REF!)')
            range_pattern_ref_2 = re.compile(r'(#REF!):([A-Za-z_\u00C0-\u017F][A-Za-z0-9_\u00C0-\u017F]*)!([A-Z]+)(\d+)')
            range_pattern_ref_3 = re.compile(r'(#REF!):(#REF!)')

            name_of_cell_to_remove = cell.name

            def update_range_1(match):
                start_col = match.group(1)
                start_row = int(match.group(2))
                return f'{start_col}{start_row}:{name_of_cell_to_remove[0]}{int(name_of_cell_to_remove[1]) - 1}'

            def update_range_2(match):
                end_col = match.group(2)
                end_row = int(match.group(3))
                return f'{name_of_cell_to_remove}:{end_col}{end_row}'

            def update_range_3(match):
                self.set_error(ErrorType.REF)
                return f'{match.group(1)}:{match.group(2)}'

            self.formula = self.formula.replace(f'{name_of_cell_to_remove}', f'{ErrorType.REF.value[0]}')
            self.formula = range_pattern_ref_1.sub(update_range_1, self.formula)
            self.formula = range_pattern_ref_2.sub(update_range_2, self.formula)
            self.formula = range_pattern_ref_3.sub(update_range_3, self.formula)

        del self.items_that_i_depend_on[cell.name]

    @property
    def name(self):
        return f"{self.spreadsheet_name}!{index_to_letter(self.column())}{self.row() + 1}"

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


class Spreadsheet:
    def __init__(self, table: QTableWidget, name: str):
        self.table_widget = table
        self.row_count = 0
        self.COLUMNS_COUNT = self.table_widget.columnCount()
        self.worksheet: List[List[SpreadsheetCell]] = [[SpreadsheetCell() for _ in range(self.COLUMNS_COUNT)] for _ in
                                                       range(0)]
        self.spreadsheet_name = name

    def add_row(self, index: int):
        if index < 0 or index > self.row_count:
            raise IndexError("Index out of range")

        self.worksheet.insert(index, [SpreadsheetCell() for _ in range(self.COLUMNS_COUNT)])
        self.row_count += 1
        self.table_widget.insertRow(index)

        for col in range(self.COLUMNS_COUNT):
            cell = self.worksheet[index][col]
            cell.spreadsheet_name = self.spreadsheet_name
            self.table_widget.setItem(index, col, cell)
        # self.reference_changed()

    def remove_row(self, index: int):
        if index < 0 or index >= self.row_count:
            return

        cells_to_remove = self.worksheet[index]

        for cell_to_remove in cells_to_remove:
            for dependent in cell_to_remove.items_that_dependents_on_me:
                dependent.remove_dependent(cell_to_remove)

        for cell_to_remove in cells_to_remove:
            for name, dependent in cell_to_remove.items_that_i_depend_on.items():
                dependent.items_that_dependents_on_me.remove(cell_to_remove)

        self.worksheet.pop(index)
        self.row_count -= 1
        self.table_widget.removeRow(index)
        # self.reference_changed()

    def get_cell(self,row,column):
        return self.worksheet[row][column]


class SpreadsheetManager:
    def __init__(self):
        self.spreadsheets: Dict[str, Spreadsheet] = {}
        self._active_spreadsheet_name: Optional[str] = None
        self._active_spreadsheet: Optional[Spreadsheet] = None
        self.dirty_cells: Set[SpreadsheetCell] = set()
        self.parser = Parser(self)

    def add_spreadsheet(self, name: str, spreadsheet_to_add: QTableWidget):
        """Add a new spreadsheet table with the given name."""
        if name in self.spreadsheets:
            raise ValueError(f"Spreadsheet with name '{name}' already exists.")
        if not isinstance(spreadsheet_to_add, QTableWidget):
            raise TypeError("table_to_add must be an instance of QTableWidget.")
        self.spreadsheets[name] = Spreadsheet(spreadsheet_to_add,name)
        if self._active_spreadsheet is None:
            self.active_spreadsheet_name = name  # Set initial active spreadsheet

    def remove_spreadsheet(self, name: str):
        """Remove the spreadsheet table with the given name."""
        if name not in self.spreadsheets:
            raise KeyError(f"No spreadsheet found with name '{name}'.")
        # If the table to be removed is the active table, clear the active table
        if name == self._active_spreadsheet_name:
            self._active_spreadsheet_name = None
            self._active_spreadsheet = None
        del self.spreadsheets[name]

    def get_spreadsheet_by_name(self, name: str) -> Optional[Spreadsheet]:
        """Retrieve the spreadsheet table with the given name."""
        if name not in self.spreadsheets:
            raise KeyError(f"No spreadsheet found with name '{name}'.")
        return self.spreadsheets[name]

    @property
    def active_spreadsheet(self) -> Optional[Spreadsheet]:
        return self._active_spreadsheet

    @active_spreadsheet.setter
    def active_spreadsheet(self, name: Optional[str]):
        if name is None:
            self._active_spreadsheet_name = None
            self._active_spreadsheet = None
        elif name not in self.spreadsheets:
            raise KeyError(f"No spreadsheet found with name '{name}'.")
        else:
            self._active_spreadsheet_name = name
            self._active_spreadsheet = self.get_spreadsheet_by_name(name)

    @property
    def active_spreadsheet_name(self) -> Optional[str]:
        return self._active_spreadsheet_name

    @active_spreadsheet_name.setter
    def active_spreadsheet_name(self, name: Optional[str]):
        if name is None:
            self.active_spreadsheet = None
        elif name not in self.spreadsheets:
            raise KeyError(f"No spreadsheet found with name '{name}'.")
        else:
            self.active_spreadsheet = name

    ####################################################################

    def get_cell(self, row, column, name_of_spreadsheet) -> Optional[SpreadsheetCell]:
        if name_of_spreadsheet in self.spreadsheets:
            return self.spreadsheets[name_of_spreadsheet].get_cell(row, column)
        return None

    def set_cell(self, row, column, formula, name_of_spreadsheet=None):
        if name_of_spreadsheet is None:
            name_of_spreadsheet = self.active_spreadsheet_name
        cell_to_set = self.get_cell(row, column, name_of_spreadsheet)
        if cell_to_set is not None:
            cell_to_set.formula = formula
            cell_to_set.set_error()
            cell_to_set.update_dependencies(self.parser.parse_formula_for_dependencies(cell_to_set.formula))

            self.mark_dirty(cell_to_set)
            self.calculate_spreadsheets()

    def mark_dirty(self, cell: SpreadsheetCell):
        """Mark a cell as dirty and propagate this state to its dependents."""
        if cell not in self.dirty_cells:
            self.dirty_cells.add(cell)
            to_process = deque([cell])
            processed = set()

            while to_process:
                current_cell = to_process.popleft()
                if current_cell not in processed:
                    processed.add(current_cell)
                    for dep in current_cell.items_that_dependents_on_me:
                        if dep not in self.dirty_cells:
                            self.dirty_cells.add(dep)
                        if dep not in processed:
                            to_process.append(dep)

    ####################################################################

    def _get_range(self, start_row: int, start_col: int, end_row: int, end_col: int, sheet_name: str) -> List[SpreadsheetCell]:
        return [self.get_cell(row, col, sheet_name) for row in range(start_row, end_row + 1) for col in range(start_col, end_col + 1)]

    def calculate_spreadsheets(self):
        """Calculate and update the values of all dirty cells."""
        if not self.dirty_cells:
            return
        non_error_cells = []

        # Detect circular dependencies
        for cell in self.dirty_cells:
            for dependent in cell.items_that_dependents_on_me:
                if cell.check_circular_dependency(dependent):
                    cell.set_error(ErrorType.CIRCULAR)
            if cell.error is None:
                non_error_cells.append(cell)

        if non_error_cells:
            order = self.topological_sort(non_error_cells)
            for cell in order:
                if cell in self.dirty_cells:
                    self.evaluate_cell_formula(cell)
                    cell.apply_formatting_to_display_value()
                    self.dirty_cells.discard(cell)

        self.dirty_cells = {cell for cell in self.dirty_cells if not cell.error}
        assert not self.dirty_cells, "Some cells are still marked as dirty after calculation."

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

    def evaluate_cell_formula(self, cell:SpreadsheetCell):
        try:
            if cell.formula.startswith('='):
                cell.error = None
                self.parser.make_python_formula(cell)
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
    def sum(cells: List['SpreadsheetCell']) -> float:
        """Sum the values of a list of cells."""
        total = 0.0
        for cell in cells:
            if is_convertible_to_float(cell.value):
                total += float(cell.value)
            else:
                # Handle non-numeric values if needed
                pass
        return total

