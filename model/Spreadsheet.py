from typing import List, Optional

from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget

from model.Enums import ErrorType
from model.ItemWithFormula import ItemWithFormula
from resources.parser import Tokenizer, TokenType, ValueType
from resources.utils import index_to_letter, is_convertible_to_float, is_valid_cell_reference, is_valid_cell_range


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
            f"Error Message: {self.error}\n"
            f"{'-' * 80}"
        )

    @property
    def name(self):
        return f"{self.tableWidget().objectName()}!{index_to_letter(self.column())}{self.row() + 1}"

    @property
    def value(self):
        if is_convertible_to_float(self._value):
            return float(self._value)
        if self._value is None:
            return 0
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self.error:
            self._value = self.error.value[0]
        self.setText(str(self.value))

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
