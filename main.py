import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QLineEdit, QStyledItemDelegate, QMainWindow, QMenu
from Spreadsheet import RowType, Spreadsheet
from main_window import Ui_MainWindow


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

        self.spreadsheet = Spreadsheet(self.PositonsTable.columnCount())
        self.quantity_column_nr = 3
        self.price_column_nr = 4
        self.netto_column_nr = 5

        self.current_row = None
        self.current_column = None

        self.original_text = ""
        self.edited_text = ""

    def init_ui(self):
        self.PositonsTable.setItemDelegate(self.delegate)

        self.delegate.cellTextChanged.connect(self.handle_cell_editing)
        self.delegate.cellRevert.connect(self.handle_cell_revert)
        self.delegate.closeEditor.connect(self.handle_cell_editing_finished)

        self.PositonsTable.cellDoubleClicked.connect(self.handle_cell_double_click)
        self.PositonsTable.currentCellChanged.connect(self.handle_current_cell_change)
        self.lineEdit.editingFinished.connect(self.handle_line_edit_editing_finished)
        self.lineEdit.textEdited.connect(self.handle_line_edit_text_edited)

        self.PositonsTable.customContextMenuRequested.connect(self.show_context_menu)
        self.PositonsTable.horizontalHeader().sectionResized.connect(self.PositonsTable.resizeRowsToContents)
        self.PositonsTable.setRowCount(0)

    def show_context_menu(self, pos: QtCore.QPoint):
        def is_valid_context_menu_position(index: QtCore.QModelIndex, pos: QtCore.QPoint) -> bool:
            if index.isValid() and index.column() == 1:
                return True
            header_left = self.PositonsTable.horizontalHeader().sectionPosition(1)
            header_width = self.PositonsTable.horizontalHeader().sectionSize(1)
            return header_left <= pos.x() <= header_left + header_width

        index = self.PositonsTable.indexAt(pos)
        if not is_valid_context_menu_position(index, pos):
            return

        menu = QMenu()
        add_root_action = menu.addAction('Dopisz root')
        add_position_action = menu.addAction('Dopisz pozycję')
        menu.addSeparator()
        delete_action = menu.addAction('Usuń...')

        action = menu.exec(self.PositonsTable.mapToGlobal(pos))
        if action:
            row = index.row() if index.isValid() else self.PositonsTable.rowCount() - 1
            if action == add_position_action:
                self.add_row(RowType.POSITION, row + 1)
            elif action == delete_action:
                self.delete_row(row)
            elif action == add_root_action:
                self.add_row(RowType.ROOT, row + 1)

    ##################################################################################

    def add_row(self, row_type: RowType, index: int):
        index = min(index, self.PositonsTable.rowCount())
        self.spreadsheet.add_row(index, self.PositonsTable.columnCount(), self.PositonsTable, row_type)

    def delete_row(self, index: int):
        self.spreadsheet.remove_row(index, self.PositonsTable)

    ##################################################################################

    def print_cell_details(self, cell):
        print(f"cell at: {self.current_row} {self.current_column}")
        print(f"VALUE: {cell.value}")
        print(f"FORMULA: {cell.formula}")
        print(f"python_formula: {cell.python_formula}")
        print(f"error_message: {cell.error_message}")
        print(f"influenced_cells: {cell.cells_on_which_i_depend}")
        print(f"depends_on: {cell.cells_that_depend_on_me}")
        print("-" * 80)

    def handle_current_cell_change(self, row: int, column: int):
        print("handle_current_cell_change")
        cell = self.spreadsheet.get_cell(row, column)
        self.current_row, self.current_column = row, column

        self.lineEdit.setText(cell.formula)
        self.original_text = cell.formula
        self.edited_text = cell.formula

        self.print_cell_details(cell)

    def handle_cell_double_click(self, row: int, column: int):
        print("handle_cell_double_click")
        cell = self.spreadsheet.get_cell(row, column)
        self.current_row, self.current_column = row, column

        self.PositonsTable.item(row, column).setText(cell.formula)
        self.lineEdit.setText(cell.formula)
        self.original_text = cell.formula
        self.edited_text = cell.formula

    ##################################################################################

    def handle_line_edit_text_edited(self, text: str):
        if self.current_row is not None and self.current_column is not None:
            print("handle_line_edit_text_edited")
            self.edited_text = text

            # temporarily show the formula in the cell (for the time of editing)
            self.PositonsTable.item(self.current_row, self.current_column).setText(text)

    def handle_line_edit_editing_finished(self):
        if self.current_row is not None and self.current_column is not None:
            print("handle_line_edit_editing_finished")
            self.spreadsheet.set_cell_formula(self.current_row, self.current_column, self.edited_text)
            self.spreadsheet.calculate_cell_value(self.current_row, self.current_column)
            self.original_text = self.edited_text

    ##################################################################################

    def handle_cell_editing(self, text: str):
        if self.current_row is not None and self.current_column is not None:
            print("handle_cell_editing")
            self.edited_text = text
            self.lineEdit.setText(text)

    def handle_cell_editing_finished(self):
        if self.current_row is not None and self.current_column is not None:
            print("handle_cell_editing_finished")
            self.spreadsheet.set_cell_formula(self.current_row, self.current_column, self.edited_text)
            self.spreadsheet.calculate_cell_value(self.current_row, self.current_column)
            self.original_text = self.edited_text

    ##################################################################################

    def handle_cell_revert(self):
        if self.original_text != self.edited_text:
            print("REVERT")
            self.edited_text = self.original_text

            self.lineEdit.setText(self.edited_text)

            cell = self.spreadsheet.get_cell(self.current_row, self.current_column)
            cell.item.setText("leave this")
            cell.item.setText(self.edited_text)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
