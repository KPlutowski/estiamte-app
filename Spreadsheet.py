import re
from typing import List, Optional, Tuple
from PyQt6 import QtGui
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


def parse_cell_location(loc: str) -> Tuple[int, int]:
    """Convert a cell location string (e.g., 'A1') into a tuple (row, column). A1 -> (0,0)."""
    match = re.match(r'([A-Z]+)(\d+)', loc)
    if not match:
        raise ValueError(f"Invalid cell location: {loc}")
    col = letter_to_index(match.group(1))
    row = int(match.group(2)) - 1
    return row, col


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
            return replace_range(re.search(range_pattern, range_str))
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


class NumberFormat(Enum):
    GENERAL = auto()
    NUMBER = auto()
    ACCOUNTING = auto()


class ErrorType(Enum):
    REF = ("#REF!", 'Invalid cell reference.')
    DIV = ('#DIV/0!', 'Division by zero.')
    NAME = ('#NAME?', 'Invalid function or range name.')
    VALUE = ('#VALUE!', 'Wrong type of argument or operand.')
    NA = ('#N/A', 'A value is not available.')
    NUM = ('#NUM!', 'Invalid numeric value.')
    NULL = ('#NULL!', 'Incorrect use of range in formula.')
    CIRCULAR = ('#CIRCULAR!', 'Circular reference detected.')


class RowType(Enum):
    UNDEFINED = auto()
    POSITION = auto()
    ROOT = auto()


class CellItem:
    def __init__(self):
        self.item = QTableWidgetItem()
        self._value = ''
        self._foreground_color = (0, 0, 0)
        self._is_bold = False
        self._format = NumberFormat.GENERAL
        self.error: Optional[ErrorType] = None

    @property
    def color(self) -> Tuple[int, int, int]:
        return self._foreground_color

    @color.setter
    def color(self, color: Tuple[int, int, int]):
        self._foreground_color = color
        self.item.setForeground(QtGui.qRgb(*self._foreground_color))

    @property
    def is_bold(self) -> bool:
        return self._is_bold

    @is_bold.setter
    def is_bold(self, is_bold: bool):
        self._is_bold = is_bold
        font = self.item.font()
        font.setBold(self._is_bold)
        self.item.setFont(font)

    @property
    def number_format(self) -> NumberFormat:
        return self._format

    @number_format.setter
    def number_format(self, number_format: NumberFormat):
        self._format = number_format
        self.apply_formatting_to_display_value()

    def apply_formatting_to_display_value(self):
        if is_convertible_to_float(self._value):
            formatted_value = self._value
            if self._format == NumberFormat.ACCOUNTING:
                formatted_value = f"{float(self._value):.2f} zł"
            elif self._format == NumberFormat.NUMBER:
                formatted_value = f"{float(self._value):.2f}"
            self.item.setText(formatted_value)
        else:
            self.item.setText(self._value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    @property
    def column(self):
        return self.item.column()

    @property
    def row(self):
        return self.item.row()

    @property
    def address(self):
        return f"{index_to_letter(self.column)}{self.row + 1}"


class SpreadsheetCell(CellItem):
    def __init__(self, spreadsheet=None):
        super().__init__()
        self.spreadsheet = spreadsheet  # Reference to the parent Spreadsheet
        self.cells_on_which_i_depend: List[Tuple['SpreadsheetCell', str]] = []  # Cells on which I depend and corresponding str
        self.cells_that_depend_on_me: List['SpreadsheetCell'] = []
        self.formula = ''  # The formula the user entered e.g., "=A1 + A2"
        self.python_formula = ''  # Formula to be executed by the program

    def __str__(self) -> str:
        """Return a string representation of the SpreadsheetCell state."""
        return (
            f"{'-' * 80}\n"
            f"Cell at: row = {self.row}, column = {self.column}\n"
            f"Address: {self.address}\n"
            f"Value: {self._value}\n"
            f"Formula: {self.formula}\n"
            f"Python Formula: {self.python_formula}\n"
            f"Error Message: {self.error}\n"
            f"Cells on which I depend: {self.cells_on_which_i_depend}\n"
            f"Cells that depend on me: {self.cells_that_depend_on_me}\n"
            f"{'-' * 80}"
        )

    def cleanup(self):
        """Cleanup dependencies when a cell is removed."""
        for dependent_cell in self.cells_that_depend_on_me:
            if self.address in dependent_cell.formula:
                dependent_cell.cells_on_which_i_depend = [
                    (None, self.address) if (self, self.address) == (dep_cell, orig_addr) else (dep_cell, orig_addr)
                    for dep_cell, orig_addr in dependent_cell.cells_on_which_i_depend
                ]
                dependent_cell.formula = dependent_cell.formula.replace(self.address, ErrorType.REF.value[0])

        for cell, _ in self.cells_on_which_i_depend:
            if cell is not None:
                cell.cells_that_depend_on_me.remove(self)

    def update_formula(self):
        """Update the formula based on changes in cell dependencies."""
        if not self.formula.startswith('='):
            return

        updated_formula = self.formula
        new_dependencies = []

        for dependent_cell, original_address in self.cells_on_which_i_depend:
            if dependent_cell is None:
                self.set_error(ErrorType.REF)
                continue

            current_address = dependent_cell.address

            old_row, old_col = parse_cell_location(original_address)
            new_row, new_col = parse_cell_location(current_address)

            if old_row != new_row or old_col != new_col:
                updated_formula = updated_formula.replace(original_address, current_address)
                new_dependencies.append((dependent_cell, current_address))
            else:
                new_dependencies.append((dependent_cell, original_address))

        self.cells_on_which_i_depend = new_dependencies
        self.formula = updated_formula

    def calculate_value(self):
        """Calculate the value of this cell by triggering the spreadsheet's calculation mechanism."""
        if self.spreadsheet:
            self.spreadsheet.calculate_cell_value(self.row, self.column)

    def set_error(self, error: ErrorType):
        self.error = error
        self.value = error.value[0]
        self.python_formula = None

        self.apply_formatting_to_display_value()

        # Notify dependent cells about the error
        for dependent_cell in self.cells_that_depend_on_me:
            if dependent_cell.error is not error:
                dependent_cell.set_error(error)


class Spreadsheet:
    def __init__(self, row_length: int):
        self.worksheet: List[List[SpreadsheetCell]] = [[SpreadsheetCell(self) for _ in range(row_length)]]
        self.row_length = row_length

    def get_cell(self, row: int, column: int) -> SpreadsheetCell:
        return self.worksheet[row][column]

    def set_cell(self, row: int, column: int, cell: SpreadsheetCell):
        self.worksheet[row][column] = cell

    def add_row(self, index: int, num_cells: int, table: QTableWidget, row_type: RowType = RowType.UNDEFINED):
        table.insertRow(index)
        self.worksheet.insert(index,[SpreadsheetCell(self) for _ in range(self.row_length)])

        default_formulas = {
            RowType.POSITION: ["SIATKA 20x20", "nie zamawiamy powyżej 150zł/h", "szt.", "8", "184.64", ""],
            RowType.ROOT: ["Kosztorys", "Przykład - kosztorys szczegółowy", "", "", "", "0"]
        }

        for column in range(num_cells):
            cell = self.get_cell(index,column)
            if row_type in default_formulas:
                formulas = default_formulas[row_type]
                if column < len(formulas):
                    cell.formula = formulas[column]
            cell.number_format = NumberFormat.ACCOUNTING
            cell.color = (255, 0, 0) if row_type == RowType.ROOT else (0, 0, 0)
            cell.is_bold = row_type == RowType.ROOT

            self.set_cell_formula(index, column, cell.formula)
            table.setItem(index, column, cell.item)
        self.update_formulas()
        self.calculate_table()

    def remove_row(self, index: int, table: QTableWidget):
        if 0 <= index < len(self.worksheet):
            for cell in self.worksheet[index]:
                cell.cleanup()
            self.worksheet.pop(index)
        table.removeRow(index)
        self.update_formulas()
        # self.calculate_table()

    @staticmethod
    def sum(cells: List[SpreadsheetCell]) -> float:
        """Calculate the sum of a range of cells."""
        return sum(
            float(cell.value) for cell in cells
            if isinstance(cell, SpreadsheetCell) and is_convertible_to_float(cell.value)
        )

    def _get_range(self, start_row: int, start_col: int, end_row: int, end_col: int) -> List[SpreadsheetCell]:
        """Get a list of cells within a specified range."""
        return [
            self.get_cell(row, col)
            for row in range(start_row, end_row + 1)
            for col in range(start_col, end_col + 1)
        ]

    ##################################################################################

    def set_cell_formula(self, row: int, column: int, formula_from_user: str):
        cell = self.get_cell(row, column)
        cell.formula = formula_from_user
        self.calculate_cell_value(row, column)

    def _evaluate_cell_formula(self, cell: SpreadsheetCell):
        """Calculate and set the value of the given cell based on its formula."""
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
            cell.set_error(ErrorType.DIV)
        except ValueError:
            cell.set_error(ErrorType.VALUE)
        except Exception as e:
            cell.set_error(ErrorType.NAME)

    ##################################################################################

    def calculate_cell_value(self, row: int, column: int):
        """Calculate the value of a cell and update dependencies, ensuring only unique dependencies are added, with circular reference checking."""

        def has_circular_dependency(_cell: SpreadsheetCell, _current_path: set) -> bool:
            """
            Check if there is a circular dependency involving the given cell.
            """
            if _cell in _current_path:
                return True
            _current_path.add(_cell)
            for _dependent_cell, _ in _cell.cells_on_which_i_depend:
                if has_circular_dependency(_dependent_cell, _current_path):
                    return True
            _current_path.remove(_cell)
            return False

        cell = self.get_cell(row, column)

        # 1. Remove previous dependencies
        for dependent_cell, _ in cell.cells_on_which_i_depend:
            if cell in dependent_cell.cells_that_depend_on_me:
                dependent_cell.cells_that_depend_on_me.remove(cell)
        cell.cells_on_which_i_depend.clear()

        # 2. Parse the formula and identify new dependencies
        if cell.formula.startswith('='):
            formula = cell.formula[1:]
            cell_ref_pattern = re.compile(r'([A-Z]+)(\d+)')
            current_path = {cell}

            unique_dependencies = set()

            for match in cell_ref_pattern.finditer(formula):
                ref_column = letter_to_index(match.group(1))
                ref_row = int(match.group(2)) - 1
                dependent_cell = self.get_cell(ref_row, ref_column)

                # Add to unique dependencies set
                if dependent_cell not in unique_dependencies:
                    unique_dependencies.add(dependent_cell)
                    # Update dependencies
                    cell.cells_on_which_i_depend.append((dependent_cell, match.group(0)))
                    dependent_cell.cells_that_depend_on_me.append(cell)

                # Circular dependency check
                if has_circular_dependency(dependent_cell, current_path):
                    cell.set_error(ErrorType.CIRCULAR)
                    return

        # 3. Evaluate the formula in this cell
        self._evaluate_cell_formula(cell)

        cell.apply_formatting_to_display_value()

        # 4. Recalculate values in cells that depend on this one
        for dependent_cell in cell.cells_that_depend_on_me:
            self.calculate_cell_value(dependent_cell.row, dependent_cell.column)

    def update_formulas(self):
        for row in self.worksheet:
            for cell in row:
                cell.update_formula()

    def calculate_table(self):
        for row in self.worksheet:
            for cell in row:
                cell.calculate_value()

