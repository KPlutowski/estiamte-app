import sys
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QLineEdit, QStyledItemDelegate, QMainWindow, QMenu,QTableWidget
from Spreadsheet import Spreadsheet,SpreadsheetManager
from main_window import Ui_MainWindow
from typing import Optional



class ItemDelegate(QStyledItemDelegate):
    cellTextChanged = QtCore.pyqtSignal(str)
    cellRevert = QtCore.pyqtSignal()

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.textEdited.connect(lambda text: self.on_editor_text_changed(index, text))
            editor.installEventFilter(self)
        return editor

    def on_editor_text_changed(self, index: QtCore.QModelIndex, text: str):
        self.cellTextChanged.emit(text)

    def revert_edit(self):
        self.cellRevert.emit()

    def eventFilter(self, obj: QtWidgets.QWidget, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_Escape:
                self.revert_edit()
                return True
        return super().eventFilter(obj, event)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.delegate = ItemDelegate(self)
        self.init_ui()
        self.current_row = None
        self.current_column = None
        self.original_text = ""
        self.edited_text = ""

        self.active_table: Optional[QTableWidget] = None
        self.spreadsheet_manager = SpreadsheetManager()
        self.init_tables()

    def init_tables(self):
        self.spreadsheet_manager.add_table(self.tabWidget.tabText(0), Spreadsheet(self.PositonsTableWidget))
        self.spreadsheet_manager.add_table(self.tabWidget.tabText(1), Spreadsheet(self.PropertiesTableWidget))
        for name,spreadsheet in self.spreadsheet_manager.spreadsheets.items():
            spreadsheet.table_widget.setItemDelegate(self.delegate)
            spreadsheet.table_widget.cellDoubleClicked['int','int'].connect(self.handle_cell_double_click)
            spreadsheet.table_widget.currentCellChanged.connect(self.handle_current_cell_change)
            spreadsheet.table_widget.customContextMenuRequested.connect(self.show_context_menu)
            spreadsheet.table_widget.horizontalHeader().sectionResized.connect(spreadsheet.table_widget.resizeRowsToContents)
            spreadsheet.table_widget.setRowCount(0)
        self.tab_changed(self.tabWidget.currentIndex())

    def init_ui(self):
        self.tabWidget.currentChanged['int'].connect(self.tab_changed)

        self.delegate.cellTextChanged.connect(self.handle_cell_editing)
        self.delegate.cellRevert.connect(self.handle_cell_revert)
        self.delegate.closeEditor.connect(self.handle_cell_editing_finished)

        self.Formula_bar.editingFinished.connect(self.handle_line_edit_editing_finished)
        self.Formula_bar.textEdited.connect(self.handle_line_edit_text_edited)

    def show_context_menu(self, pos: QtCore.QPoint):
        index = self.active_table.indexAt(pos)
        if index.isValid():
            return

        menu = QMenu()
        add_position_action = menu.addAction('Dopisz pozycję')
        menu.addSeparator()
        delete_action = menu.addAction('Usuń...')

        action = menu.exec(self.active_table.mapToGlobal(pos))
        if action:
            row = index.row() if index.isValid() else self.active_table.rowCount() - 1
            if action == add_position_action:
                self.add_row( row + 1)
            elif action == delete_action:
                self.delete_row(row)

    def tab_changed(self, index):
        self.spreadsheet_manager.active_spreadsheet = self.tabWidget.tabText(index)
        self.active_table = self.spreadsheet_manager.active_spreadsheet.table_widget

    ##################################################################################

    def add_row(self,index: int):
        index = min(index, self.active_table.rowCount())
        self.spreadsheet_manager.active_spreadsheet.add_row(index)

    def delete_row(self, index: int):
        self.spreadsheet_manager.active_spreadsheet.remove_row(index)

    ##################################################################################

    def handle_current_cell_change(self, row: int, column: int):
        print("handle_current_cell_change")
        if 0 <= row < self.spreadsheet_manager.active_spreadsheet.row_count:
            cell = self.spreadsheet_manager.active_spreadsheet.get_cell(row, column)
            self.current_row, self.current_column = row, column

            self.Formula_bar.setText(cell.formula)
            self.Name_box.setText(cell.name)
            self.original_text = cell.formula
            self.edited_text = cell.formula
            print(cell)

    def handle_cell_double_click(self, row: int, column: int):
        print("handle_cell_double_click")
        cell = self.spreadsheet_manager.active_spreadsheet.get_cell(row, column)
        self.current_row, self.current_column = row, column

        self.active_table.item(row, column).setText(cell.formula)
        self.Formula_bar.setText(cell.formula)
        self.original_text = cell.formula
        self.edited_text = cell.formula

    ##################################################################################

    def handle_line_edit_text_edited(self, text: str):
        if self.current_row is not None and self.current_column is not None:
            print("handle_line_edit_text_edited")
            self.edited_text = text

            # temporarily show the formula in the cell (for the time of editing)
            self.active_table.item(self.current_row, self.current_column).setText(text)

    def handle_line_edit_editing_finished(self):
        if self.current_row is not None and self.current_column is not None:
            print("handle_line_edit_editing_finished")
            self.spreadsheet_manager.active_spreadsheet.set_cell_formula(self.current_row, self.current_column, self.edited_text)
            self.original_text = self.edited_text

    ##################################################################################

    def handle_cell_editing(self, text: str):
        if self.current_row is not None and self.current_column is not None:
            print("handle_cell_editing")
            self.edited_text = text
            self.Formula_bar.setText(text)

    def handle_cell_editing_finished(self):
        if self.current_row is not None and self.current_column is not None:
            print("handle_cell_editing_finished")
            self.spreadsheet_manager.active_spreadsheet.set_cell_formula(self.current_row, self.current_column, self.edited_text)
            self.original_text = self.edited_text

    ##################################################################################

    def handle_cell_revert(self):
        if self.original_text != self.edited_text:
            print("REVERT")
            self.edited_text = self.original_text

            self.Formula_bar.setText(self.edited_text)

            cell = self.spreadsheet_manager.active_spreadsheet.get_cell(self.current_row, self.current_column)
            cell.item.setText("leave this")
            cell.item.setText(self.edited_text)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

