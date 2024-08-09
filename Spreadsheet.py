# Spreadsheet.py
import re
from PyQt6 import QtGui
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget
from enum import Enum


def is_float(value):
    """Check if the value can be converted to a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


class NumberFormat(Enum):
    GENERAL = 0
    NUMBER = 1
    ACCOUNTING = 2


class RowType(Enum):
    NO_TYPE = 0
    POSITION = 1
    ROOT_ELEMENT = 2


class Cell:
    def __init__(self):
        self._foreground_color = (0, 0, 0)
        self._is_bold = False
        self._error_message = None
        self._format = NumberFormat.GENERAL

        self.edit_mode = False

        self._value = ''
        self._user_formula = ''
        self._evaluated_formula = ''

        self._item = QTableWidgetItem()

    @property
    def color(self):
        return self._foreground_color

    @color.setter
    def color(self, color):
        self._foreground_color = color
        self._item.setForeground(QtGui.qRgb(*self._foreground_color))

    @property
    def is_bold(self):
        return self._is_bold

    @is_bold.setter
    def is_bold(self, is_bold):
        self._is_bold = is_bold
        font = QFont()
        font.setBold(self._is_bold)
        self._item.setFont(font)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def number_format(self):
        return self._format

    @number_format.setter
    def number_format(self, number_format: NumberFormat):
        self._format = number_format

    @property
    def user_formula(self):
        return self._user_formula

    @user_formula.setter
    def user_formula(self, formula):
        self._user_formula = formula

    @property
    def evaluated_formula(self):
        return self._evaluated_formula

    @evaluated_formula.setter
    def evaluated_formula(self, formula):
        self._evaluated_formula = formula

    @property
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, error):
        self._error_message = error

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, new_item):
        self._item = new_item


class Row:
    def __init__(self, num_cells, row_type: RowType = RowType.NO_TYPE):
        self.cells = [Cell() for _ in range(num_cells)]
        self.row_type = row_type
        self._set_row_defaults()

    def _set_row_defaults(self):
        if self.row_type == RowType.POSITION:

            default_formula = ["SIATKA 20x20", "nie zamawiamy powyżej 150zł/h", "szt.", "8", "184.64"]

            for column, formula in enumerate(default_formula):
                self.set_user_formula(column, formula)

            self.color = (0, 0, 0)
            self.is_bold = False
            self._set_number_formats([NumberFormat.GENERAL] * 3 + [NumberFormat.NUMBER] + [NumberFormat.ACCOUNTING] * 2)
        elif self.row_type == RowType.ROOT_ELEMENT:
            default_formula = ["Kosztorys", "Przykład - kosztorys szczegółowy", "", "", "", "0"]

            for column, formula in enumerate(default_formula):
                self.set_user_formula(column, formula)

            self.color = (255, 0, 0)
            self.is_bold = True
            self._set_number_formats([NumberFormat.GENERAL] * 3 + [NumberFormat.NUMBER] + [NumberFormat.ACCOUNTING] * 2)
        else:
            self.values = ["noType", "noType"]
            self.color = (255, 255, 0)
            self.is_bold = True

    def set_value(self, column, value):
        self.cells[column].value = value

    def get_value(self, column):
        return self.cells[column].value

    def set_user_formula(self, column, formula):
        self.cells[column].user_formula = formula

    def get_user_formula(self, column):
        return self.cells[column].user_formula

    def _set_number_formats(self, formats):
        for cell, format in zip(self.cells, formats):
            cell.number_format = format

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        for cell in self.cells:
            cell.color = color

    @property
    def is_bold(self):
        return self._is_bold

    @is_bold.setter
    def is_bold(self, is_bold):
        self._is_bold = is_bold
        for cell in self.cells:
            cell.is_bold = is_bold

    def set_evaluated_formula(self, column, formula):
        self.cells[column].evaluated_formula = formula

    def get_evaluated_formula(self, column):
        return self.cells[column].evaluated_formula

    def set_error_message(self, column, error):
        self.cells[column].error_message = error

    def get_error_message(self, column):
        return self.cells[column].error_message


class Spreadsheet:
    def __init__(self):
        self._rows = []

    def insert_row(self, index, num_cells, table: QTableWidget, row_type: RowType = RowType.NO_TYPE):
        table.insertRow(index)

        self._rows.insert(index, Row(num_cells, row_type))
        for column in range(num_cells):
            self.set_cell_formula(index, column, self.get_formula(index, column))  # default formula
            table.setItem(index, column, self.get_item(index, column))

        self.update_table()

    def delete_row(self, index, table: QTableWidget):
        table.removeRow(index)
        if 0 <= index < len(self._rows):
            self._rows.pop(index)
        self.update_table()

    def update_table(self):
        for row_idx, row in enumerate(self._rows):
            for column_idx in range(len(row.cells)):
                self.update_cell(row_idx, column_idx)

    def update_cell(self, row, column):
        value = self.get_value(row, column)
        self.get_item(row, column).setText(value)

        number_format = self.get_number_format(row, column)
        if is_float(value) and not self.get_cell_editing_state(row, column):
            if number_format == NumberFormat.GENERAL:
                self.get_item(row, column).setText(value)

            elif number_format == NumberFormat.ACCOUNTING:
                self.get_item(row, column).setText(f"{float(value):.2f} zł")

            elif number_format == NumberFormat.NUMBER:
                self.get_item(row, column).setText( f"{float(value):.2f}")
        else:
            self.get_item(row, column).setText(value)

    def set_cell_formula(self, row, column, formula_from_user):
        if formula_from_user.startswith("=") and not self.get_cell_editing_state(row, column):
            self._set_formula_and_evaluate(row, column, formula_from_user)
        else:
            self._set_value_without_formula(row, column, formula_from_user)
        self.update_cell(row, column)

    def _set_formula_and_evaluate(self, row, column, formula_from_user):
        python_formula = self._convert_to_python_formula(formula_from_user[1:])
        self.set_formula(row, column, formula_from_user)

        try:
            value = str(eval(python_formula))
            self.set_value(row, column, value)
            self.set_error(row, column, None)
        except Exception as e:
            self.set_value(row, column, str(e))
            self.set_error(row, column, str(e))

    def _set_value_without_formula(self, row, column, formula_from_user):
        self.set_formula(row, column, formula_from_user)
        self.set_value(row, column, formula_from_user)
        self.set_error(row, column, None)

    def _convert_to_python_formula(self, formula):
        pattern = r'([A-Z]+)(\d+)'
        matches = re.findall(pattern, formula)

        for col_str, row_str in matches:
            col_idx = self._column_letter_to_index(col_str)
            row_idx = int(row_str) - 1

            if 0 <= row_idx < len(self._rows) and 0 <= col_idx < len(self._rows[row_idx].cells):
                cell_value = self.get_value(row_idx, col_idx)
                formula = formula.replace(f"{col_str}{row_str}", self._format_value(cell_value))
            else:
                formula = formula.replace(f"{col_str}{row_str}", '""')

        return formula

    @staticmethod
    def _format_value(value):
        return value if is_float(value) else f'"{value}"'

    @staticmethod
    def _column_letter_to_index(letter):
        index = 0
        for char in letter:
            index = index * 26 + (ord(char.upper()) - ord('A'))
        return index

    @property
    def rows(self):
        return self._rows

    def get_value(self, row, column):
        return self._rows[row].get_value(column)

    def set_value(self, row, column, value):
        self._rows[row].set_value(column, value)

    def get_formula(self, row, column):
        return self._rows[row].get_user_formula(column)

    def set_formula(self, row, column, value):
        self._rows[row].set_user_formula(column, value)

    def get_python_formula(self, row, column):
        return self._rows[row].get_evaluated_formula(column)

    def set_python_formula(self, row, column, value):
        self._rows[row].set_evaluated_formula(column, value)

    def get_error(self, row, column):
        return self._rows[row].get_error_message(column)

    def set_error(self, row, column, value):
        self._rows[row].set_error_message(column, value)

    def set_cell_editing_state(self, row, column, is_editing):
        self._rows[row].cells[column].edit_mode = is_editing

    def get_cell_editing_state(self, row, column):
        return self._rows[row].cells[column].edit_mode

    def get_number_format(self, row, column):
        return self._rows[row].cells[column].number_format

    def get_item(self, row, column):
        return self._rows[row].cells[column].item



