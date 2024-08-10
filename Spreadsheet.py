import re
from typing import List, Optional, Tuple
from PyQt6 import QtGui
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget
from enum import Enum, auto


def convert_excel_formula_to_python(formula: str) -> str:
    """
    Convert an Excel-like formula to a Python formula that references worksheet cells.

    Example:
        Excel formula: "=SUM(A1:A3)"
        Python formula: "self.sum(self.get_range(0,0,2,0))"
    """
    # Regular expression to find cell references in the format like A1, B2, etc.
    cell_ref_pattern = re.compile(r'([A-Z]+)(\d+)')
    range_pattern = re.compile(r'([A-Z]+)(\d+):([A-Z]+)(\d+)')
    function_pattern = re.compile(r'(\w+)\(([A-Z]+\d+(:[A-Z]+\d+)?)\)')

    def replace_match(match):
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

    # Substitute all occurrences of the patterns in the formula
    formula = function_pattern.sub(replace_function, formula)
    python_formula = cell_ref_pattern.sub(replace_match, formula)

    return python_formula


def extract_dependencies_from_formula(formula: str) -> List[str]:
    """
    Parse the formula and extract unique cell references, including those in ranges.
    """
    dependencies = set()  # Use a set to avoid duplicate entries
    cell_ref_pattern = re.compile(r'([A-Z]+)(\d+)')
    range_pattern = re.compile(r'([A-Z]+)(\d+):([A-Z]+)(\d+)')

    # Extract single cell references
    cell_matches = cell_ref_pattern.findall(formula)
    for match in cell_matches:
        col = match[0]
        row = match[1]
        dependencies.add(f"{col}{row}")

    # Extract ranges
    range_matches = range_pattern.findall(formula)
    for start_col, start_row, end_col, end_row in range_matches:
        start_row = int(start_row)
        end_row = int(end_row)
        start_col_index = letter_to_index(start_col)
        end_col_index = letter_to_index(end_col)
        start_row_index = start_row - 1
        end_row_index = end_row - 1

        # Add all cells within the range
        for row in range(start_row_index, end_row_index + 1):
            for col in range(start_col_index, end_col_index + 1):
                col_letter = index_to_letter(col)
                dependencies.add(f"{col_letter}{row + 1}")

    return list(dependencies)


def is_convertible_to_float(value: str) -> bool:
    """Check if the given string can be converted to a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def letter_to_index(letter: str) -> int:
    index = 0
    for char in letter:
        index = index * 26 + (ord(char.upper()) - ord('A'))
    return index


def index_to_letter(index: int) -> str:
    """
    Convert a zero-based column index to an Excel-like column letter.
    """
    letter = ''
    while index >= 0:
        letter = chr(index % 26 + ord('A')) + letter
        index = index // 26 - 1
    return letter


def parse_cell_location(loc: str) -> Tuple[int, int]:
    """
    Convert a cell location string (e.g., 'A1') into a tuple (row, column).
    """
    match = re.match(r'([A-Z]+)(\d+)', loc)
    if not match:
        raise ValueError(f"Invalid cell location: {loc}")
    col = letter_to_index(match.group(1))
    row = int(match.group(2)) - 1
    return (row, col)


class NumberFormat(Enum):
    GENERAL = auto()
    NUMBER = auto()
    ACCOUNTING = auto()


class RowType(Enum):
    UNDEFINED = auto()
    POSITION = auto()
    ROOT = auto()


class SpreadsheetCell:
    def __init__(self):
        self._foreground_color = (0, 0, 0)
        self._is_bold = False
        self._format = NumberFormat.GENERAL
        self.edit_mode = False
        self._value = ''
        self._formula = ''
        self._python_formula = ''
        self.influenced_cells = []
        self.depends_on = []
        self._error_message: Optional[str] = None
        self._item = QTableWidgetItem()

    @property
    def color(self) -> tuple[int, int, int]:
        return self._foreground_color

    @color.setter
    def color(self, color: tuple[int, int, int]):
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
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value
        self.apply_formatting_to_display_value()

    @property
    def number_format(self) -> NumberFormat:
        return self._format

    @number_format.setter
    def number_format(self, number_format: NumberFormat):
        self._format = number_format
        self.apply_formatting_to_display_value()

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    @error_message.setter
    def error_message(self, error: Optional[str]):
        self._error_message = error

    @property
    def python_formula(self) -> Optional[str]:
        return self._python_formula

    @python_formula.setter
    def python_formula(self, python_formula: Optional[str]):
        self._python_formula = python_formula

    @property
    def item(self) -> QTableWidgetItem:
        return self._item

    @item.setter
    def item(self, new_item: QTableWidgetItem):
        self._item = new_item

    @property
    def formula(self) -> str:
        return self._formula

    @formula.setter
    def formula(self, user_input: str):
        self._formula = user_input

    def apply_formatting_to_display_value(self):
        if is_convertible_to_float(self.value) and not self.edit_mode:
            if self.number_format == NumberFormat.GENERAL:
                self.item.setText(self.value)
            elif self.number_format == NumberFormat.ACCOUNTING:
                self.item.setText(f"{float(self.value):.2f} zł")
            elif self.number_format == NumberFormat.NUMBER:
                self.item.setText(f"{float(self.value):.2f}")
        else:
            self.item.setText(self.value)

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
            RowType.POSITION: ["SIATKA 20x20", "nie zamawiamy powyżej 150zł/h", "szt.", "8", "184.64", "", "", ""],
            RowType.ROOT: ["Kosztorys", "Przykład - kosztorys szczegółowy", "", "", "", "0", "", ""]
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
            for col_idx, cell in enumerate(row):
                location = (row_idx, col_idx)
                self.visited_cells = set()  # Reset visited cells for each calculation
                self.calculate_cell_value(*location)

    def calculate_cell_value(self, row: int, column: int):
        """
        Calculates the value of a cell and updates its dependencies.
        """
        cell = self.get_cell(row, column)

        if cell.edit_mode:
            return
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
        old_dependencies = set(cell.depends_on)
        new_dependencies_set = set(new_dependencies)

        cell.depends_on = new_dependencies

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

                # Check if the referenced cell is within the valid range of the worksheet
                if dep_row < len(self.worksheet) and dep_column < len(self.worksheet[dep_row]):
                    dependent_cell = self.get_cell(dep_row, dep_column)
                    cell_ref = f"{chr(cell.item.column() + 65)}{cell.item.row() + 1}"
                    if cell_ref in dependent_cell.influenced_cells:
                        dependent_cell.influenced_cells.remove(cell_ref)
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
        if cell_ref not in dependent_cell.influenced_cells:
            dependent_cell.influenced_cells.append(cell_ref)

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
        cells = []
        for r_idx, _row in enumerate(self.worksheet):
            for c_idx, cell in enumerate(_row):
                if f"{chr(column + 65)}{row + 1}" in cell.depends_on:
                    cells.append((r_idx, c_idx))
        return cells

    def sum(self, cells: List[SpreadsheetCell]) -> float:
        """Calculate the sum of a range of cells."""
        total = 0
        for cell in cells:
            if isinstance(cell, SpreadsheetCell):
                try:
                    total += float(cell.value)
                except ValueError:
                    pass  # Ignore non-numeric values
        return total

    def get_range(self, start_row: int, start_col: int, end_row: int, end_col: int) -> List[SpreadsheetCell]:
        """Get a list of cells within a specified range."""
        cells = []
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                cells.append(self.get_cell(row, col))
        return cells
