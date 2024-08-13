import re
from typing import List, Optional, Dict, Set
from collections import deque, defaultdict
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget
from enum import Enum, auto


def index_to_letter(index: int) -> str:
    """Convert a zero-based column index to an Excel-like column letter."""
    letter = ''
    while index >= 0:
        letter = chr(index % 26 + ord('A')) + letter
        index = index // 26 - 1
    return letter


def letter_to_index(letter: str) -> int:
    """Convert an Excel column letter to a zero-based column index."""
    index = 0
    for char in letter.upper():
        index = index * 26 + (ord(char) - ord('A'))
    return index


def convert_excel_formula_to_python(formula: str) -> str:
    """Convert an Excel-like formula to a Python formula."""
    cell_ref_pattern = re.compile(r'([A-Z]+)(\d+)')
    range_pattern = re.compile(r'([A-Z]+)(\d+):([A-Z]+)(\d+)')
    function_pattern = re.compile(r'(\w+)\(([A-Z]+\d+(:[A-Z]+\d+)?)\)')

    def replace_cell(match):
        column_letter = match.group(1)
        row_number = int(match.group(2))
        column_index = letter_to_index(column_letter)
        row_index = row_number - 1
        return f'float(self.get_cell({row_index},{column_index}).value)'

    def replace_range(match):
        start_col = match.group(1)
        start_row = int(match.group(2))
        end_col = match.group(3)
        end_row = int(match.group(4))
        start_col_index = letter_to_index(start_col)
        end_col_index = letter_to_index(end_col)
        start_row_index = start_row - 1
        end_row_index = end_row - 1
        return f'self.sum(self._get_range({start_row_index}, {start_col_index}, {end_row_index}, {end_col_index}))'

    def replace_function(match):
        function_name = match.group(1).lower()
        if function_name == 'sum':
            range_str = match.group(2)
            range_match = range_pattern.match(range_str)
            if range_match:
                return replace_range(range_match)
            else:
                return 'self.sum([])'  # Default to an empty list if range is invalid
        return match.group(0)

    formula = function_pattern.sub(replace_function, formula)
    return cell_ref_pattern.sub(replace_cell, formula)


def is_convertible_to_float(value: str) -> bool:
    """Check if the given string can be converted to a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


class ErrorType(Enum):
    REF = ("#REF!", 'Invalid cell reference.')
    DIV = ('#DIV/0!', 'Division by zero.')
    NAME = ('#NAME?', 'Invalid function or range name.')
    VALUE = ('#VALUE!', 'Wrong type of argument or operand.')
    NA = ('#N/A', 'A value is not available.')
    NUM = ('#NUM!', 'Invalid numeric value.')
    NULL = ('#NULL!', 'Incorrect use of range in formula.')
    CIRCULAR = ('#CIRCULAR!', 'Circular reference detected.')


class SpreadsheetCell:
    def __init__(self, spreadsheet=None):
        self.item = QTableWidgetItem()
        self.value = ''
        self.error: Optional[ErrorType] = None
        self.spreadsheet = spreadsheet
        self.formula = ''
        self.python_formula = ''
        self.cells_that_i_dependents_on_and_names: Dict[SpreadsheetCell, str] = {}  # Maps dependent cells to the names or ranges
        self.cells_that_dependents_on_me: List[SpreadsheetCell] = []  # List of cells that dependents on me

    def __str__(self) -> str:
        return (
            f"{'-' * 80}\n"
            f"Cell at: row = {self.row}, column = {self.column}, Name: {self.name}\n"
            f"self: {hex(id(self))}\n"
            f"Value: {self.value}, Formula: {self.formula}\n"
            f"Python_formula: {self.python_formula}\n"
            f"cells_that_i_dependents_on_and_names: {self.cells_that_i_dependents_on_and_names}\n"
            f"cells_that_dependents_on_me: {self.cells_that_dependents_on_me}\n"
            f"Error Message: {self.error}, Python Formula: {self.python_formula}\n"
            f"{'-' * 80}"
        )

    def apply_formatting_to_display_value(self):
        if self.error:
            self.item.setText(self.error.value[0])
        else:
            self.item.setText(self.value)

    @property
    def column(self):
        return self.item.column()

    @property
    def row(self):
        return self.item.row()

    @property
    def name(self):
        return f"{index_to_letter(self.column)}{self.row + 1}"

    def add_dependent(self, cell: 'SpreadsheetCell', reference_name: str):
        self.cells_that_i_dependents_on_and_names[cell] = reference_name

    def remove_dependent(self, cell: 'SpreadsheetCell'):
        if cell in self.cells_that_i_dependents_on_and_names:
            if self.formula.find(self.cells_that_i_dependents_on_and_names.get(cell)) != -1:
                range_pattern_ref_1 = re.compile(r'([A-Z]+)(\d+):(#REF!)')
                range_pattern_ref_2 = re.compile(r'(#REF!):([A-Z]+)(\d+)')
                range_pattern_ref_3 = re.compile(r'(#REF!):(#REF!)')
                name_of_cell_to_remove = self.cells_that_i_dependents_on_and_names.get(cell)

                def update_range_1(match):
                    start_col = match.group(1)
                    start_row = int(match.group(2))
                    return f'{start_col}{start_row}:{name_of_cell_to_remove[0]}{int(name_of_cell_to_remove[1]) - 1}'

                def update_range_2(match):
                    end_col = match.group(2)
                    end_row = int(match.group(3))
                    return f'{name_of_cell_to_remove}:{end_col}{end_row}'

                def update_range_3(match):
                    self.update_error(ErrorType.REF)
                    return f'{match.group(1)}:{match.group(2)}'

                self.formula = self.formula.replace(f'{name_of_cell_to_remove}', f'{ErrorType.REF.value[0]}')
                self.formula = range_pattern_ref_1.sub(update_range_1, self.formula)
                self.formula = range_pattern_ref_2.sub(update_range_2, self.formula)
                self.formula = range_pattern_ref_3.sub(update_range_3, self.formula)

            del self.cells_that_i_dependents_on_and_names[cell]

    def update_error(self, error: Optional[ErrorType] = None):
        """Update the error state of this cell and propagate the change to dependent cells. """
        if error is not None:
            # Set error
            self.error = error
            self.python_formula = None
            self.value = error.value[0]
            self.apply_formatting_to_display_value()

            for cell in self.cells_that_dependents_on_me:
                if cell.error is None:
                    cell.update_error(error)
        else:
            # Reset error
            self.error = None
            self.python_formula = None
            self.value = ''
            self.apply_formatting_to_display_value()

            for cell in self.cells_that_dependents_on_me:
                if cell.error is not None:
                    cell.update_error(None)


class Spreadsheet:
    def __init__(self, table: QTableWidget):
        self.table_widget = table
        self.row_count = 0
        self.COLUMNS_COUNT = self.table_widget.columnCount()
        self.worksheet: List[List[SpreadsheetCell]] = [[SpreadsheetCell(self) for _ in range(self.COLUMNS_COUNT)] for _ in
                                                       range(0)]
        self.dirty_cells: Set[SpreadsheetCell] = set()

    def get_cell(self, row: int, column: int) -> SpreadsheetCell:
        return self.worksheet[row][column]

    def add_row(self, index: int, num_cells: int):
        if index < 0 or index > self.row_count:
            raise IndexError("Index out of range")

        self.worksheet.insert(index, [SpreadsheetCell(self) for _ in range(num_cells)])
        self.row_count += 1
        self.table_widget.insertRow(index)

        for col in range(num_cells):
            cell = self.get_cell(index, col)
            self.table_widget.setItem(index, col, cell.item)
        self.reference_changed()

    def remove_row(self, index: int):
        if index < 0 or index >= self.row_count:
            return

        cells_to_remove = self.worksheet[index]

        for cell_to_remove in cells_to_remove:
            for dependent in list(cell_to_remove.cells_that_dependents_on_me):
                dependent.remove_dependent(cell_to_remove)

        for cell_to_remove in cells_to_remove:
            for dependent, _ in cell_to_remove.cells_that_i_dependents_on_and_names.items():
                dependent.cells_that_dependents_on_me.remove(cell_to_remove)

        self.worksheet.pop(index)
        self.row_count -= 1
        self.table_widget.removeRow(index)
        self.reference_changed()

    ##################################################################################

    @staticmethod
    def sum(cells: List[SpreadsheetCell]) -> float:
        """Sum the values of a list of cells."""
        total = 0.0
        for cell in cells:
            if is_convertible_to_float(cell.value):
                total += float(cell.value)
            else:
                # Handle non-numeric values if needed
                pass
        return total

    def _get_range(self, start_row: int, start_col: int, end_row: int, end_col: int) -> List[SpreadsheetCell]:
        return [self.get_cell(row, col) for row in range(start_row, end_row + 1) for col in
                range(start_col, end_col + 1)]

    def parse_formula(self, formula: str) -> List[SpreadsheetCell]:
        """Parse formula and return a list of dependent cells."""
        dependencies = []
        cell_ref_pattern = re.compile(r'([A-Z]+)(\d+)')
        range_pattern = re.compile(r'([A-Z]+)(\d+):([A-Z]+)(\d+)')

        for match in cell_ref_pattern.finditer(formula):
            ref_column = letter_to_index(match.group(1))
            ref_row = int(match.group(2)) - 1
            dependencies.append(self.get_cell(ref_row, ref_column))

        for match in range_pattern.finditer(formula):
            start_col = letter_to_index(match.group(1))
            start_row = int(match.group(2)) - 1
            end_col = letter_to_index(match.group(3))
            end_row = int(match.group(4)) - 1
            range_cells = self._get_range(start_row, start_col, end_row, end_col)
            dependencies.extend(range_cells)

        return dependencies

    def worksheet_cell_set(self) -> Set[SpreadsheetCell]:
        """Return a set of all cells in the worksheet."""
        return {cell for row in self.worksheet for cell in row}

    ##################################################################################

    def set_cell_formula(self, row: int, column: int, formula_from_user: str):
        cell = self.get_cell(row, column)
        cell.formula = formula_from_user
        cell.update_error()
        cell.python_formula = convert_excel_formula_to_python(formula_from_user)
        self.update_dependencies(cell)
        self.mark_dirty(cell)
        self.calculate_table()

    def update_dependencies(self, cell: SpreadsheetCell):
        self.remove_all_dependencies(cell)
        if cell.formula.startswith('='):
            formula = cell.formula[1:]
            new_dependencies = self.parse_formula(formula)
            self.add_dependencies(cell, new_dependencies)

    @staticmethod
    def add_dependencies(cell: SpreadsheetCell, dependencies: List[SpreadsheetCell]):
        for dep_cell in dependencies:
            if cell not in dep_cell.cells_that_dependents_on_me:
                dep_cell.cells_that_dependents_on_me.append(cell)
            cell.add_dependent(dep_cell, dep_cell.name)

    @staticmethod
    def remove_all_dependencies(cell: SpreadsheetCell):
        for dep in cell.cells_that_i_dependents_on_and_names:
            dep.cells_that_dependents_on_me.remove(cell)
        cell.cells_that_i_dependents_on_and_names.clear()

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
                    for dep in current_cell.cells_that_dependents_on_me:
                        if dep not in self.dirty_cells:
                            self.dirty_cells.add(dep)
                        if dep not in processed:
                            to_process.append(dep)

    @staticmethod
    def check_circular_dependency(start_cell: SpreadsheetCell, target_cell: SpreadsheetCell) -> bool:
        """Check if there is a circular dependency from target_cell to start_cell."""
        stack = [target_cell]
        visited = set()

        while stack:
            cell = stack.pop()
            if cell == start_cell:
                return True
            if cell not in visited:
                visited.add(cell)
                stack.extend(cell.cells_that_dependents_on_me)
        return False

    ##################################################################################

    def calculate_table(self):
        """Calculate and update the values of all dirty cells."""
        if not self.dirty_cells:
            return
        non_error_cells = []

        # Detect circular dependencies
        for cell in self.dirty_cells:
            for dependent in cell.cells_that_dependents_on_me:
                if self.check_circular_dependency(cell, dependent):
                    cell.update_error(ErrorType.CIRCULAR)
            if cell.error is None:
                non_error_cells.append(cell)
        if non_error_cells:
            order = self.topological_sort(non_error_cells)
            for cell in order:
                if cell in self.dirty_cells:
                    self._evaluate_cell_formula(cell)
                    cell.apply_formatting_to_display_value()
                    self.dirty_cells.discard(cell)

        self.dirty_cells = {cell for cell in self.dirty_cells if not cell.error}
        assert not self.dirty_cells, "Some cells are still marked as dirty after calculation."

    def _evaluate_cell_formula(self, cell: SpreadsheetCell):
        try:
            if cell.formula.startswith('='):
                cell.python_formula = convert_excel_formula_to_python(cell.formula[1:])
                cell.value = str(eval(cell.python_formula, {'self': self}))
                cell.error = None
            else:
                cell.value = cell.formula
                cell.python_formula = None
                cell.error = None
        except ZeroDivisionError:
            cell.update_error(ErrorType.DIV)
        except ValueError:
            cell.update_error(ErrorType.VALUE)
        except (SyntaxError, NameError):
            cell.update_error(ErrorType.NAME)
        except Exception:
            cell.update_error(ErrorType.NAME)

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
            for dependent in cell.cells_that_dependents_on_me:
                if dependent in cells:
                    in_degree[dependent] += 1

        # Initialize queue with cells that have zero in-degree
        zero_in_degree = deque(cell for cell in cells if in_degree[cell] == 0)
        topological_order = []

        while zero_in_degree:
            cell = zero_in_degree.popleft()
            topological_order.append(cell)
            for dependent in cell.cells_that_dependents_on_me:
                if dependent in cells:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        zero_in_degree.append(dependent)

        if len(topological_order) != len(cells):
            raise RuntimeError("Cyclic dependency detected")
        return topological_order

    def reference_changed(self):
        """Update cell references and addresses when the position of cells changes."""
        cell_ref_pattern = re.compile(r'([A-Z]+)(\d+)')

        affected_cells = set()
        for row in self.worksheet:
            for cell in row:
                if cell.formula.startswith('='):
                    affected_cells.add(cell)

        for cell in affected_cells:
            formula = cell.formula[1:]

            def update_reference(match):
                column_letter = match.group(1)
                row_number = int(match.group(2))
                for depend, name in cell.cells_that_i_dependents_on_and_names.items():
                    if name == f'{column_letter}{row_number}':
                        return f'{depend.name}'
                return f"{column_letter}{row_number}"

            updated_formula = cell_ref_pattern.sub(update_reference, formula)

            cell.formula = '=' + updated_formula
            cell.python_formula = convert_excel_formula_to_python(updated_formula)
            self.update_dependencies(cell)
            self.mark_dirty(cell)
        self.calculate_table()


class TableManager:
    def __init__(self):
        pass