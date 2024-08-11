import re
from typing import List, Optional, Tuple
from PyQt6 import QtGui
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget
from enum import Enum, auto


def convert_excel_formula_to_python(formula: str) -> str:
    """
    Convert an Excel-like formula to a Python formula that references worksheet cells.
    """
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
        return f'self.sum(self.get_range({start_row_index}, {start_col_index}, {end_row_index}, {end_col_index}))'

    def replace_function(match):
        function_name = match.group(1).lower()
        if function_name == 'sum':
            range_str = match.group(2)
            return replace_range(re.search(range_pattern, range_str))
        return match.group(0)

    formula = function_pattern.sub(replace_function, formula)
    return cell_ref_pattern.sub(replace_cell, formula)


def extract_dependencies_from_formula(formula: str) -> List[str]:
    """
    Parse the formula and extract unique cell references, including those in ranges.
    """
    dependencies = set()
    cell_ref_pattern = re.compile(r'([A-Z]+)(\d+)')
    range_pattern = re.compile(r'([A-Z]+)(\d+):([A-Z]+)(\d+)')

    # Extract single cell references
    for match in cell_ref_pattern.findall(formula):
        col, row = match
        dependencies.add(f"{col}{row}")

    # Extract ranges
    for start_col, start_row, end_col, end_row in range_pattern.findall(formula):
        start_row, end_row = int(start_row), int(end_row)
        start_col_index = letter_to_index(start_col)
        end_col_index = letter_to_index(end_col)
        start_row_index = start_row - 1
        end_row_index = end_row - 1

        dependencies.update(
            f"{index_to_letter(col)}{row + 1}"
            for row in range(start_row_index, end_row_index + 1)
            for col in range(start_col_index, end_col_index + 1)
        )

    return list(dependencies)


def is_convertible_to_float(value: str) -> bool:
    """Check if the given string can be converted to a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def letter_to_index(letter: str) -> int:
    """Convert an Excel column letter to a zero-based column index."""
    index = 0
    for char in letter.upper():
        index = index * 26 + (ord(char) - ord('A'))
    return index


def index_to_letter(index: int) -> str:
    """Convert a zero-based column index to an Excel-like column letter."""
    letter = ''
    while index >= 0:
        letter = chr(index % 26 + ord('A')) + letter
        index = index // 26 - 1
    return letter


def parse_cell_location(loc: str) -> Tuple[int, int]:
    """Convert a cell location string (e.g., 'A1') into a tuple (row, column)."""
    match = re.match(r'([A-Z]+)(\d+)', loc)
    if not match:
        raise ValueError(f"Invalid cell location: {loc}")
    col = letter_to_index(match.group(1))
    row = int(match.group(2)) - 1
    return row, col


class NumberFormat(Enum):
    GENERAL = auto()
    NUMBER = auto()
    ACCOUNTING = auto()


class RowType(Enum):
    UNDEFINED = auto()
    POSITION = auto()
    ROOT = auto()


class CellItem:
    def __init__(self):
        self._item = QTableWidgetItem()
        self._value = ''  # THE VALUE THAT WILL BE DISPLAYED AFTER DECORATORS ARE ADDED e.g. "string", "123", "1a2b3c
        self._foreground_color = (0, 0, 0)
        self._is_bold = False
        self._format = NumberFormat.GENERAL
        self._error_message: Optional[str] = None

    @property
    def color(self) -> Tuple[int, int, int]:
        return self._foreground_color

    @color.setter
    def color(self, color: Tuple[int, int, int]):
        self._foreground_color = color
        self._item.setForeground(QtGui.qRgb(*self._foreground_color))

    @property
    def is_bold(self) -> bool:
        return self._is_bold

    @is_bold.setter
    def is_bold(self, is_bold: bool):
        self._is_bold = is_bold
        font = self._item.font()
        font.setBold(self._is_bold)
        self._item.setFont(font)

    @property
    def number_format(self) -> NumberFormat:
        return self._format

    @number_format.setter
    def number_format(self, number_format: NumberFormat):
        self._format = number_format
        self.apply_formatting_to_display_value()

    def apply_formatting_to_display_value(self):
        if is_convertible_to_float(self._value):
            if self._format == NumberFormat.GENERAL:
                self._item.setText(self._value)
            elif self._format == NumberFormat.ACCOUNTING:
                self._item.setText(f"{float(self._value):.2f} zł")
            elif self._format == NumberFormat.NUMBER:
                self._item.setText(f"{float(self._value):.2f}")
        else:
            self._item.setText(self._value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value
        self.apply_formatting_to_display_value()

    @property
    def item(self) -> QTableWidgetItem:
        return self._item

    @item.setter
    def item(self, new_item: QTableWidgetItem):
        self._item = new_item

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    @error_message.setter
    def error_message(self, error: Optional[str]):
        self._error_message = error


class SpreadsheetCell(CellItem):
    def __init__(self):
        super().__init__()

        self.cells_on_which_i_depend: List[str] = []  # e.g. A1,B3 etc..
        self.cells_that_depend_on_me: List[str] = []

        self._formula = ''  # THE FORMULA THE USER ENTERED e.g. "=A1+A2"
        self._python_formula = ''  # FORMULA TO BE EXECUTED BY THE PROGRAM

        self.row = None  # Row number of the cell in reference.
        self.col = None  # Column number of the cell in reference.

    @property
    def python_formula(self) -> Optional[str]:
        return self._python_formula

    @python_formula.setter
    def python_formula(self, python_formula: Optional[str]):
        self._python_formula = python_formula

    @property
    def formula(self) -> str:
        return self._formula

    @formula.setter
    def formula(self, user_input: str):
        self._formula = user_input

    def process_and_set_formula(self, user_input: str):
        self.formula = user_input
        if self.formula.startswith('='):
            try:
                self.value = user_input
                self.python_formula = convert_excel_formula_to_python(user_input[1:])
                self.error_message = None
            except Exception as e:
                self.value = str(e)
                self.python_formula = None
                self.error_message = str(e)
        else:
            self.value = user_input
            self.python_formula = None
            self.error_message = None


class Spreadsheet:
    def __init__(self, row_length: int):
        self.worksheet: List[List[SpreadsheetCell]] = [[SpreadsheetCell() for _ in range(row_length)]]
        self.row_length = row_length
        self.visited_cells = set()

    def _ensure_row_exists(self, index: int, num_cells: int):
        """Ensure the worksheet has enough rows and cells."""
        while len(self.worksheet) <= index:
            self.worksheet.append([SpreadsheetCell() for _ in range(self.row_length)])
        for row in self.worksheet:
            if len(row) < num_cells:
                row.extend(SpreadsheetCell() for _ in range(num_cells - len(row)))

    def get_cell(self, row: int, column: int) -> SpreadsheetCell:
        return self.worksheet[row][column]

    def set_cell(self, row: int, column: int, cell: SpreadsheetCell):
        self.worksheet[row][column] = cell

    def add_row(self, index: int, num_cells: int, table: QTableWidget, row_type: RowType = RowType.UNDEFINED):
        table.insertRow(index)
        self._ensure_row_exists(index, num_cells)

        default_formulas = {
            RowType.POSITION: ["SIATKA 20x20", "nie zamawiamy powyżej 150zł/h", "szt.", "8", "184.64", ""],
            RowType.ROOT: ["Kosztorys", "Przykład - kosztorys szczegółowy", "", "", "", "0"]
        }

        for column in range(num_cells):
            cell = SpreadsheetCell()
            if row_type in default_formulas:
                formulas = default_formulas[row_type]
                if column < len(formulas):
                    cell.formula = formulas[column]
            cell.number_format = NumberFormat.ACCOUNTING
            cell.color = (255, 0, 0) if row_type == RowType.ROOT else (0, 0, 0)
            cell.is_bold = row_type == RowType.ROOT

            self.set_cell(index, column, cell)
            self.set_cell_formula(index, column, cell.formula)
            table.setItem(index, column, cell.item)

    def remove_row(self, index: int, table: QTableWidget):
        table.removeRow(index)
        if 0 <= index < len(self.worksheet):
            self.worksheet.pop(index)

    def set_cell_formula(self, row: int, column: int, formula_from_user: str):
        self.get_cell(row, column).process_and_set_formula(formula_from_user)

    def calculate_all(self):
        for row_idx, row in enumerate(self.worksheet):
            for col_idx, _ in enumerate(row):
                self.visited_cells = set()  # Reset visited cells for each calculation
                self.calculate_cell_value(row_idx, col_idx)

    def calculate_cell_value(self, row: int, column: int):
        """
        Calculate the value of a cell and update its dependencies.
        """
        cell = self.get_cell(row, column)

        if not (0 <= row < len(self.worksheet) and 0 <= column < len(self.worksheet[row])):
            cell.value = "Error: Cell reference out of range"
            cell.apply_formatting_to_display_value()
            return

        cell_ref = f"{chr(column + 65)}{row + 1}"
        if cell_ref in self.visited_cells:
            cell.value = "#CYCLE!"
            cell.apply_formatting_to_display_value()
            return

        # Mark the cell as visited to detect potential cycles
        self.visited_cells.add(cell_ref)

        self._update_cell_dependencies(cell)
        self._calculate_cell_value(cell)
        self._calculate_dependent_cells(row, column)

        # Unmark the cell as visited after calculation
        self.visited_cells.remove(cell_ref)

    def _update_cell_dependencies(self, cell: SpreadsheetCell):
        """
        Update the dependencies of the given cell and manage the influenced cells.
        """
        new_dependencies = extract_dependencies_from_formula(cell.formula[1:])
        old_dependencies = set(cell.cells_that_depend_on_me)
        new_dependencies_set = set(new_dependencies)

        cell.cells_that_depend_on_me = new_dependencies

        self._remove_old_dependencies(cell, old_dependencies - new_dependencies_set)

        # Add new dependencies, ensuring they are within range
        for dependency in new_dependencies:
            try:
                dep_row, dep_column = parse_cell_location(dependency)
                if (0 <= dep_row < len(self.worksheet) and
                        0 <= dep_column < len(self.worksheet[dep_row])):
                    self._add_new_dependency(cell, dep_row, dep_column)
            except ValueError:
                continue  # Skip invalid cell references

    def _remove_old_dependencies(self, cell: SpreadsheetCell, old_dependencies: set):
        """
        Remove the old dependencies from the influenced cells.
        """
        for dependency in old_dependencies:
            try:
                dep_row, dep_column = parse_cell_location(dependency)
                if dep_row < len(self.worksheet) and dep_column < len(self.worksheet[dep_row]):
                    dependent_cell = self.get_cell(dep_row, dep_column)
                    cell_ref = f"{chr(cell.item.column() + 65)}{cell.item.row() + 1}"
                    if cell_ref in dependent_cell.cells_on_which_i_depend:
                        dependent_cell.cells_on_which_i_depend.remove(cell_ref)
                else:
                    print(f"Warning: Cell reference {dependency} is out of range. Skipping removal of dependency.")
            except IndexError:
                print(f"Error: Invalid cell reference {dependency} during dependency removal.")
                continue

    def _add_new_dependency(self, cell: SpreadsheetCell, dep_row: int, dep_column: int):
        """
        Add a new dependency to the influenced cells of the given cell.
        """
        dependent_cell = self.get_cell(dep_row, dep_column)
        cell_ref = f"{chr(cell.item.column() + 65)}{cell.item.row() + 1}"
        if cell_ref not in dependent_cell.cells_on_which_i_depend:
            dependent_cell.cells_on_which_i_depend.append(cell_ref)

    def _calculate_cell_value(self, cell: SpreadsheetCell):
        """
        Calculate and set the value of the given cell based on its formula.
        """
        if cell.python_formula:
            try:
                cell.value = str(eval(cell.python_formula, {'self': self}))
                cell.error_message = None
            except Exception as e:
                cell.value = str(e)
                cell.error_message = str(e)
        cell.apply_formatting_to_display_value()

    def _calculate_dependent_cells(self, row: int, column: int):
        """
        Recalculate the values of cells that depend on the given cell.
        """
        for dep_row, dep_column in self.get_dependent_cells(row, column):
            self.calculate_cell_value(dep_row, dep_column)
            self.get_cell(dep_row, dep_column).apply_formatting_to_display_value()

    def get_dependent_cells(self, row: int, column: int) -> List[Tuple[int, int]]:
        """
        Get a list of cells that depend on the cell located at (row, column).
        """
        return [
            (r_idx, c_idx)
            for r_idx, _row in enumerate(self.worksheet)
            for c_idx, cell in enumerate(_row)
            if f"{chr(column + 65)}{row + 1}" in cell.cells_that_depend_on_me
        ]

    @staticmethod
    def sum(cells: List[SpreadsheetCell]) -> float:
        """Calculate the sum of a range of cells."""
        return sum(
            float(cell.value) for cell in cells
            if isinstance(cell, SpreadsheetCell) and is_convertible_to_float(cell.value)
        )

    def get_range(self, start_row: int, start_col: int, end_row: int, end_col: int) -> List[SpreadsheetCell]:
        """Get a list of cells within a specified range."""
        return [
            self.get_cell(row, col)
            for row in range(start_row, end_row + 1)
            for col in range(start_col, end_col + 1)
        ]
