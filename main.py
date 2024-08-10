# main.py
import sys
from PyQt6.QtWidgets import QLineEdit
from PyQt6 import QtCore, QtWidgets
from Spreadsheet import RowType, Spreadsheet
from main_window import Ui_MainWindow


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    cellEditingStarted = QtCore.pyqtSignal(int, int)
    cellEditingFinished = QtCore.pyqtSignal(int, int, str)

    def createEditor(self, parent, option, index):
        editor = super(ItemDelegate, self).createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.textChanged.connect(lambda text: self.on_editor_text_changed(index, text))
            editor.editingFinished.connect(lambda: self.commit_and_close_editor(editor, index))
            # editor.returnPressed
            # editor.textEdited
        return editor

    def commit_and_close_editor(self, editor, index):
        self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.EndEditHint.NoHint)

    def on_editor_text_changed(self, index, text):
        self.cellEditingFinished.emit(index.row(), index.column(), text)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.delegate = ItemDelegate(self)

        self.init_ui()

        self.spreadsheet = Spreadsheet(self.PositonsTable.columnCount())
        self.quantity_column_nr = 3
        self.price_column_nr = 4
        self.netto_column_nr = 5

        self.current_row = None
        self.current_column = None

    def init_ui(self):
        self.PositonsTable.setItemDelegate(self.delegate)

        self.delegate.cellEditingFinished.connect(self.cell_editing_handler)
        self.delegate.closeEditor.connect(self.cell_editing_finished_handler)

        self.PositonsTable.cellDoubleClicked.connect(self.cell_double_clicked_handler)
        self.PositonsTable.currentCellChanged.connect(self.current_cell_changed_handler)
        self.lineEdit.editingFinished.connect(self.line_edit_editing_finished_handler)
        self.lineEdit.textEdited.connect(self.line_edit_editing_handler)

        self.PositonsTable.customContextMenuRequested.connect(self.on_context_menu)
        self.PositonsTable.horizontalHeader().sectionResized.connect(self.PositonsTable.resizeRowsToContents)
        self.PositonsTable.setRowCount(0)

    def on_context_menu(self, pos):
        index = self.PositonsTable.indexAt(pos)

        valid_column = index.isValid() and index.column() == 1
        # if you need to get the menu for that column, no matter if a row exists
        if not valid_column:
            left = self.PositonsTable.horizontalHeader().sectionPosition(1)
            width = self.PositonsTable.horizontalHeader().sectionSize(1)
            if left <= pos.x() <= left + width:
                valid_column = True

        if valid_column:
            menu = QtWidgets.QMenu()

            add_root = menu.addAction('Dopisz root')
            add_position = menu.addAction('Dopisz pozycję')
            menu.addSeparator()
            delete = menu.addAction('Usuń...')

            action = menu.exec(self.PositonsTable.mapToGlobal(pos))
            if action:
                if not index.isValid():
                    # If click POSITION is invalid, set the index to the last row
                    index = self.PositonsTable.model().index(self.PositonsTable.rowCount() - 1, 0)
                row = index.row()
                if action == add_position:
                    self.add_row(RowType.POSITION, row + 1)
                elif action == delete:
                    self.delete_row(row)
                elif action == add_root:
                    self.add_row(RowType.ROOT, row + 1)

    def add_row(self, _type: RowType, index):
        index = min(index, self.PositonsTable.rowCount())
        self.spreadsheet.add_row(index, self.PositonsTable.columnCount(), self.PositonsTable, _type)

    def delete_row(self, index):
        self.spreadsheet.remove_row(index, self.PositonsTable)

    def cell_double_clicked_handler(self, row, column):
        # print("cell_double_clicked_handler")
        formula = self.spreadsheet.get_cell(row, column).formula
        self.PositonsTable.item(row, column).setText(formula)

    def current_cell_changed_handler(self, row, column):
        print("cell at: ", row, " ", column)
        print("VALUE: ", self.spreadsheet.get_cell(row, column).value)
        print("FORMULA: ", self.spreadsheet.get_cell(row, column).formula)
        print("python_formula: ", self.spreadsheet.get_cell(row, column).python_formula)
        print("error_message: ", self.spreadsheet.get_cell(row, column).error_message)
        print("influenced_cells: ", self.spreadsheet.get_cell(row, column).influenced_cells)
        print("depends_on: ", self.spreadsheet.get_cell(row, column).depends_on)
        print("------------------------------------------------------------------------------")

        # Update lineEdit with the formula or value of the clicked cell
        self.current_row = row
        self.current_column = column
        formula = self.spreadsheet.get_cell(row, column).formula
        self.lineEdit.setText(formula)

    def line_edit_editing_handler(self, text):
        # print("line_edit_editing_handler")
        if self.current_row is not None and self.current_column is not None:
            self.spreadsheet.get_cell(self.current_row, self.current_column).edit_mode = True
            self.spreadsheet.set_cell_formula(self.current_row, self.current_column, text)

    def cell_editing_handler(self, row, column, text):
        # print("cell_editing_handler")
        if self.current_row is not None and self.current_column is not None:
            self.spreadsheet.get_cell(self.current_row, self.current_column).edit_mode = True
            self.spreadsheet.set_cell_formula(self.current_row, self.current_column, text)
            self.lineEdit.setText(self.spreadsheet.get_cell(self.current_row, self.current_column).formula)

    def line_edit_editing_finished_handler(self):
        # print("line_edit_editing_finished_handler")
        if self.current_row is not None and self.current_column is not None:
            self.spreadsheet.get_cell(self.current_row, self.current_column).edit_mode = False
            self.spreadsheet.calculate_cell_value(self.current_row, self.current_column)

    def cell_editing_finished_handler(self):
        # print("cell_editing_finished_handler")
        if self.current_row is not None and self.current_column is not None:
            self.spreadsheet.get_cell(self.current_row, self.current_column).edit_mode = False
            self.spreadsheet.calculate_cell_value(self.current_row, self.current_column)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
