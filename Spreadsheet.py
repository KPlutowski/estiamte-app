import re
from typing import List, Optional
from PyQt6 import QtGui
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget
from enum import Enum, auto


def is_float(value: str) -> bool:
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


class RowType(Enum):
    NO_TYPE = auto()
    POSITION = auto()
    ROOT_ELEMENT = auto()


class Cell:
    def __init__(self):
        self._foreground_color = (0, 0, 0)
        self._is_bold = False
        self._format = NumberFormat.GENERAL
        self.edit_mode = False
        self._value = ''
        self._user_formula = ''
        self._python_formula = ''
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
        self.update_cell()

    @property
    def number_format(self) -> NumberFormat:
        return self._format

    @number_format.setter
    def number_format(self, number_format: NumberFormat):
        self._format = number_format
        self.update_cell()

    @property
    def user_formula(self) -> str:
        return self._user_formula

    @user_formula.setter
    def user_formula(self, formula: str):
        self._user_formula = formula

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    @error_message.setter
    def error_message(self, error: Optional[str]):
        self._error_message = error

    @property
    def item(self) -> QTableWidgetItem:
        return self._item

    @item.setter
    def item(self, new_item: QTableWidgetItem):
        self._item = new_item

    def update_cell(self):
        if is_float(self.value) and not self.edit_mode:
            if self.number_format == NumberFormat.GENERAL:
                self.item.setText(self.value)
            elif self.number_format == NumberFormat.ACCOUNTING:
                self.item.setText(f"{float(self.value):.2f} zł")
            elif self.number_format == NumberFormat.NUMBER:
                self.item.setText(f"{float(self.value):.2f}")
        else:
            self.item.setText(self.value)


class Spreadsheet:
    def __init__(self, row_length: int):
        self.worksheet: List[List[Cell]] = [[Cell() for _ in range(row_length)]]
        self.row_length = row_length

    def get_cell(self, row: int, column: int) -> Cell:
        return self.worksheet[row][column]

    def set_cell(self, row: int, column: int, cell: Cell):
        self.worksheet[row][column] = cell

    def insert_row(self, index: int, num_cells: int, table: QTableWidget, row_type: RowType = RowType.NO_TYPE):
        table.insertRow(index)
        self._ensure_row_exists(index, num_cells)

        default_formulas = {
            RowType.POSITION: ["SIATKA 20x20", "nie zamawiamy powyżej 150zł/h", "szt.", "8", "184.64", "", "", ""],
            RowType.ROOT_ELEMENT: ["Kosztorys", "Przykład - kosztorys szczegółowy", "", "", "", "0", "", ""]
        }

        for column in range(num_cells):
            cell = Cell()
            if row_type in default_formulas:
                formulas = default_formulas[row_type]
                if column < len(formulas):
                    cell.user_formula = formulas[column]
            cell.number_format = NumberFormat.GENERAL
            cell.color = (255, 0, 0) if row_type == RowType.ROOT_ELEMENT else (0, 0, 0)
            cell.is_bold = row_type == RowType.ROOT_ELEMENT

            self.set_cell(index, column, cell)
            self.set_cell_formula(index, column, cell.user_formula)
            table.setItem(index, column, cell.item)

        self.update_table()

    def delete_row(self, index: int, table: QTableWidget):
        table.removeRow(index)
        if 0 <= index < len(self.worksheet):
            self.worksheet.pop(index)
        self.update_table()

    def update_table(self):
        for row in self.worksheet:
            for cell in row:
                cell.update_cell()

    def set_cell_formula(self, row: int, column: int, formula_from_user: str):
        if formula_from_user.startswith("=") and not self.get_cell(row, column).edit_mode:
            self._set_formula_and_evaluate(row, column, formula_from_user)
        else:
            self._set_value_without_formula(row, column, formula_from_user)

    def _set_formula_and_evaluate(self, row: int, column: int, formula_from_user: str):
        python_formula = self._convert_to_python_formula(formula_from_user[1:])
        cell = self.get_cell(row, column)
        cell.user_formula = formula_from_user
        try:
            value = str(eval(python_formula))
            cell.value = value
            cell.error_message = None
        except Exception as e:
            cell.value = str(e)
            cell.error_message = str(e)

    def _set_value_without_formula(self, row: int, column: int, value: str):
        cell = self.get_cell(row, column)
        cell.user_formula = value
        cell.value = value
        cell.error_message = None

    def _convert_to_python_formula(self, formula: str) -> str:
        pattern = r'([A-Z]+)(\d+)'
        matches = re.findall(pattern, formula)

        for col_str, row_str in matches:
            col_idx = self._column_letter_to_index(col_str)
            row_idx = int(row_str) - 1

            if 0 <= row_idx < len(self.worksheet) and 0 <= col_idx < self.row_length:
                cell_value = self.get_cell(row_idx, col_idx).value
                formula = formula.replace(f"{col_str}{row_str}", self._format_value(cell_value))
            else:
                formula = formula.replace(f"{col_str}{row_str}", '""')

        return formula

    @staticmethod
    def _format_value(value: str) -> str:
        return value if is_float(value) else f'"{value}"'

    @staticmethod
    def _column_letter_to_index(letter: str) -> int:
        index = 0
        for char in letter:
            index = index * 26 + (ord(char.upper()) - ord('A'))
        return index

    def _ensure_row_exists(self, index: int, num_cells: int):
        """Ensure the worksheet has enough rows and cells."""
        while len(self.worksheet) <= index:
            self.worksheet.append([Cell() for _ in range(self.row_length)])
        for row in self.worksheet:
            if len(row) < num_cells:
                row.extend(Cell() for _ in range(num_cells - len(row)))
