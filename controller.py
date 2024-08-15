# controller.py
from typing import Optional

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QTableWidget, QMenu
from Spreadsheet import SpreadsheetManager


class Controller:
    def __init__(self, main_window: QtWidgets.QMainWindow, spreadsheet_manager: SpreadsheetManager):
        self.main_window = main_window
        self.spreadsheet_manager = spreadsheet_manager
        self.active_table: Optional[QTableWidget] = None
        self.current_row: Optional[int] = None
        self.current_column: Optional[int] = None
        self.original_text = ""
        self.edited_text = ""
        self.init_ui()

    def init_ui(self):
        self.main_window.tabWidget.currentChanged.connect(self.tab_changed)
        self.main_window.delegate.cellTextChanged.connect(self.handle_cell_editing)
        self.main_window.delegate.cellRevert.connect(self.handle_cell_revert)
        self.main_window.delegate.closeEditor.connect(self.handle_cell_editing_finished)
        self.main_window.Formula_bar.editingFinished.connect(self.handle_line_edit_editing_finished)
        self.main_window.Formula_bar.textEdited.connect(self.handle_line_edit_text_edited)


    def tab_changed(self, index: int):
        """Update active spreadsheet when tab is changed."""
        self.spreadsheet_manager.active_spreadsheet = self.main_window.tabWidget.tabText(index)
        self.active_table = self.spreadsheet_manager.active_spreadsheet.table_widget
        self.current_column = 0
        self.current_row = 0

    def handle_current_cell_change(self, row: int, column: int):
        """Handle the event when the current cell changes."""
        if 0 <= row < self.spreadsheet_manager.active_spreadsheet.row_count:
            cell = self.spreadsheet_manager.active_spreadsheet.get_cell(row, column)
            self.current_row, self.current_column = row, column
            self.main_window.Formula_bar.setText(cell.formula)
            self.main_window.Name_box.setText(cell.name)
            self.original_text = cell.formula
            self.edited_text = cell.formula

    def handle_cell_double_click(self, row: int, column: int):
        """Handle the event when a cell is double-clicked."""
        cell = self.spreadsheet_manager.active_spreadsheet.get_cell(row, column)
        self.current_row, self.current_column = row, column
        self.active_table.item(row, column).setText(cell.formula)
        self.main_window.Formula_bar.setText(cell.formula)
        self.original_text = cell.formula
        self.edited_text = cell.formula

    def handle_line_edit_text_edited(self, text: str):
        """Handle the event when the text in the formula bar is edited."""
        if self.current_row is not None and self.current_column is not None:
            self.edited_text = text
            self.active_table.item(self.current_row, self.current_column).setText(text)

    def handle_line_edit_editing_finished(self):
        """Handle the event when editing in the formula bar is finished."""
        if self.current_row is not None and self.current_column is not None:
            self.spreadsheet_manager.set_cell(self.current_row, self.current_column, self.edited_text)
            self.original_text = self.edited_text

    def handle_cell_editing(self, text: str):
        """Handle the event when cell text is edited via delegate."""
        if self.current_row is not None and self.current_column is not None:
            self.edited_text = text
            self.main_window.Formula_bar.setText(text)

    def handle_cell_editing_finished(self):
        """Handle the event when cell editing via delegate is finished."""
        if self.current_row is not None and self.current_column is not None:
            self.spreadsheet_manager.set_cell(self.current_row, self.current_column, self.edited_text)
            self.original_text = self.edited_text

    def handle_cell_revert(self):
        """Handle the event when cell editing is reverted."""
        if self.original_text != self.edited_text:
            self.edited_text = self.original_text
            self.main_window.Formula_bar.setText(self.edited_text)
            cell = self.spreadsheet_manager.active_spreadsheet.get_cell(self.current_row, self.current_column)
            cell.setText(self.edited_text)

    def show_context_menu(self, pos: QtCore.QPoint):
        index = self.active_table.indexAt(pos)
        if not index.isValid():
            return

        menu = QMenu()
        add_position_action = menu.addAction('Dopisz pozycję')
        menu.addSeparator()
        delete_action = menu.addAction('Usuń...')

        action = menu.exec(self.active_table.mapToGlobal(pos))
        if action:
            row = index.row() if index.isValid() else self.active_table.rowCount() - 1
            if action == add_position_action:
                row = min(row + 1, self.active_table.rowCount())
                self.spreadsheet_manager.active_spreadsheet.add_row(row)
            elif action == delete_action:
                self.spreadsheet_manager.active_spreadsheet.remove_row(row)
