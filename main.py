# main.py
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QStyledItemDelegate,
    QFileDialog, QTableWidgetItem, QMenu, QLineEdit
)
from PyQt6 import QtCore, QtGui, QtWidgets

from Spreadsheet import RowType, Spreadsheet
from main_window import Ui_MainWindow
from new_cost_estimate_window import Ui_new_cost_estimate_window


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    cellEditingStarted = QtCore.pyqtSignal(int, int)
    cellEditingFinished = QtCore.pyqtSignal(int, int, str)

    def createEditor(self, parent, option, index):
        editor = super(ItemDelegate, self).createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.textChanged.connect(lambda text: self.on_editor_text_changed(index, text))
            editor.editingFinished.connect(lambda: self.commit_and_close_editor(editor, index))  # Ensure to commit changes
            self.cellEditingStarted.emit(index.row(), index.column())
            self.parent().spreadsheet.set_cell_editing_state(index.row(), index.column(), True)
        return editor

    def setModelData(self, editor, model, index):
        super(ItemDelegate, self).setModelData(editor, model, index)
        text = editor.text()
        self.cellEditingFinished.emit(index.row(), index.column(), text)
        self.parent().spreadsheet.set_cell_editing_state(index.row(), index.column(), False)

    def commit_and_close_editor(self, editor, index):
        """Helper method to commit the editor's data and close it."""
        # self.setModelData(editor, self.parent().model(), index)
        self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.EndEditHint.NoHint)

    def on_editor_text_changed(self, index, text):
        self.cellEditingFinished.emit(index.row(), index.column(), text)


class new_cost_estimate(QtWidgets.QWidget, Ui_new_cost_estimate_window):
    def __init__(self):
        super(new_cost_estimate, self).__init__()
        self.setupUi(self)
        self.Change_directory_button.clicked.connect(self.action_change_directory_handler)

    # TODO
    def action_change_directory_handler(self):
        print("action_change_directory_handler")

    # TODO
    def accept(self):
        print("accept")

    # TODO
    def reject(self):
        print("reject")


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.delegate = ItemDelegate(self)

        self.init_ui()

        self.spreadsheet = Spreadsheet()
        self.quantity_column_nr = 3
        self.price_column_nr = 4
        self.netto_column_nr = 5

        self.current_row = None
        self.current_column = None

    def init_ui(self):
        self.PositonsTable.setItemDelegate(self.delegate)

        # Connecting cellEditingFinished to the handler
        self.delegate.cellEditingFinished.connect(self.cell_editing_handler)

        # Other handlers
        self.PositonsTable.cellDoubleClicked.connect(self.cell_double_clicked_handler)
        self.PositonsTable.currentCellChanged.connect(self.current_cell_changed_handler)
        self.PositonsTable.cellActivated.connect(self.cell_activated_handler)

        # LINEEDIT HANDLERS CONNECTING
        self.lineEdit.editingFinished.connect(self.handle_line_editing_finished)
        self.lineEdit.textEdited.connect(self.line_edit_text_changed_handler)
        # END OF HANDLERS

        self.PositonsTable.customContextMenuRequested.connect(self.on_context_menu)
        self.PositonsTable.horizontalHeader().sectionResized.connect(self.PositonsTable.resizeRowsToContents)
        self.PositonsTable.setRowCount(0)

        self.actionNew.triggered.connect(self.action_new_handler)
        self.actionOpen.triggered.connect(self.action_open_handler)
        self.actionSave.triggered.connect(self.action_save_handler)
        self.actionClose.triggered.connect(self.action_close_handler)
        self.actionExport_xlsx.triggered.connect(self.action_export_xlsx_handler)
        self.actionImport_xlm.triggered.connect(self.action_import_xlm_handler)
        self.actionSave_as.triggered.connect(self.action_save_as_handler)
        self.actionImportCsv.triggered.connect(self.action_import_csv_handler)
        self.actionExportCsv.triggered.connect(self.action_export_csv_handler)

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
                    self.add_row(RowType.ROOT_ELEMENT, row + 1)

    def add_row(self, _type: RowType, index):
        index = min(index, self.PositonsTable.rowCount())
        self.spreadsheet.insert_row(index, self.PositonsTable.columnCount(), self.PositonsTable, _type)

    def delete_row(self, index):
        self.spreadsheet.delete_row(index,self.PositonsTable)

    def cell_double_clicked_handler(self, row, column):
        print("cell_double_clicked_handler")
        # Display the formula in the table if it exists
        formula = self.spreadsheet.get_formula(row, column)
        if formula:
            self.PositonsTable.item(row, column).setText(formula)
        else:
            self.PositonsTable.item(row, column).setText(self.spreadsheet.get_value(row, column))

    def cell_editing_handler(self, row, column, text):
        print("cell_editing_handler")
        if row == self.current_row and column == self.current_column:
            self.spreadsheet.set_cell_formula(row, column, text)
            self.spreadsheet.set_cell_editing_state(self.current_row, self.current_column, True)
            self.lineEdit.setText(self.spreadsheet.get_formula(row, column))

    def cell_activated_handler(self, row, column):
        print("cellActivated")
        if self.current_row is not None and self.current_column is not None:
            self.spreadsheet.set_cell_editing_state(self.current_row, self.current_column, False)
            self.spreadsheet.set_cell_formula(self.current_row, self.current_column, self.lineEdit.text())

    def current_cell_changed_handler(self, row, column):
        print("current_cell_changed_handler")
        # print(self.spreadsheet.get_value(row, column))
        # print(self.spreadsheet.get_value(row, column))

        # Update lineEdit with the formula or value of the clicked cell
        self.current_row = row
        self.current_column = column

        # Get the formula if it exists, otherwise, get the value
        formula = self.spreadsheet.get_formula(row, column)
        if formula:
            self.lineEdit.setText(formula)
        else:
            self.lineEdit.setText(self.spreadsheet.get_value(row, column))

    def handle_line_editing_finished(self):
        print("handle_line_editing_finished")
        # This function is called when editing is finished
        text = self.lineEdit.text()
        if self.current_row is not None and self.current_column is not None:
            self.spreadsheet.set_cell_editing_state(self.current_row, self.current_column, False)
            self.spreadsheet.set_cell_formula(self.current_row, self.current_column, text)

    def line_edit_text_changed_handler(self, text):
        print("line_edit_text_changed_handler")
        if self.current_row is not None and self.current_column is not None:
            self.spreadsheet.set_cell_editing_state(self.current_row, self.current_column, True)
            self.spreadsheet.set_cell_formula(self.current_row, self.current_column, text)







    # TODO
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open file', '',
                                                   "CSV Files (*.csv *.tsv *.txt);;All Files (*.*)")
        if file_name:
            self.csv_file = file_name
            self.load_csv(self.csv_file)
            self.statusbar.showMessage(f"{file_name} loaded")

    # TODO
    def load_csv(self, filename):
        csv_text = open(filename, "r", encoding="UTF-8").read()
        tab_counter = csv_text.splitlines()[0].count("\t")
        comma_counter = csv_text.splitlines()[0].count(",")
        if tab_counter > comma_counter:
            self.PositonsTable.setColumnCount(tab_counter + 1)
            delimiter = "\t"
        else:
            self.PositonsTable.setColumnCount(comma_counter + 1)
            delimiter = ","
        row = 0
        for list_row in csv_text.splitlines():
            self.PositonsTable.insertRow(row)
            row_text = list_row.split(delimiter)
            column = 0
            for cell in row_text:
                cell_text = QTableWidgetItem(cell)
                self.PositonsTable.setItem(row, column, cell_text)
                column += 1
            row += 1

    # TODO
    def save_file(self):
        if self.PositonsTable.rowCount() < 1:
            return
        if self.csv_file != "":
            file_name = self.csv_file
        else:
            file_name = "*.csv"

        fname, _ = QFileDialog.getSaveFileName(self, 'Save file', file_name,
                                               "CSV Files (*.csv *.tsv *.txt);;All Files (*.*)")
        if fname:
            self.save_csv(fname)
            self.csv_file = fname

    # TODO
    def save_csv(self, filename):
        row_text = ""
        for row in range(self.PositonsTable.rowCount() - 1):

            for column in range(self.PositonsTable.columnCount() - 1):
                cell_text = self.PositonsTable.item(row, column).text()
                row_text += f"{cell_text}\t"
            row_text = row_text.rstrip("\t")
            row_text += "\n"
        with open(filename, "w", encoding="UTF-8") as f:
            f.write(row_text)

    # TODO
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == QtCore.Qt.Key.Key_C and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.copy_row()
        elif event.key() == QtCore.Qt.Key.Key_V and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.paste_row()

    # TODO
    def copy_row(self):
        pass
        # current_row = self.PositonsTable.currentRow()
        # self.PositonsTable.clearSelection()
        # self.PositonsTable.selectRow(current_row)
        # copied_cells = sorted(self.PositonsTable.selectedIndexes())
        # copy_text = ''
        #
        # for c in copied_cells:
        #     if self.PositonsTable.item(c.row(), c.column()):
        #         copy_text += self.PositonsTable.item(c.row(), c.column()).text()
        #         if c.column() == self.PositonsTable.columnCount() - 1:
        #             copy_text += '\n'
        #         else:
        #             copy_text += '\t'
        #     else:
        #         copy_text += '\t'
        # QApplication.clipboard().setText(copy_text)

    # TODO
    def paste_row(self):
        pass
        # rows = QApplication.clipboard().text().split('\n')
        # row = rows[0].split('\t')
        # if len(row) == 0:
        #     return
        #
        # row_to_paste = self.PositonsTable.currentRow() + 1
        # self.PositonsTable.clearSelection()
        # self.PositonsTable.selectRow(row_to_paste - 1)
        # self.add_row(RowType.POSITION)
        #
        # for i, value in enumerate(row):
        #     item = QtWidgets.QTableWidgetItem(value)
        #     self.PositonsTable.setItem(row_to_paste, i, item)

    # TODO
    def action_import_csv_handler(self):
        self.open_file()

    # TODO
    def action_export_csv_handler(self):
        self.save_file()

    # TODO
    def action_open_handler(self):
        # filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        # with open(filename[0], 'r') as f:
        #     file_text = f.read()
        #     self.text.setText(file_text)
        print("action_open_handler")

    # TODO
    def action_save_handler(self):
        print("action_save_handler")

    # TODO
    def action_close_handler(self):
        print("action_close_handler")

    # TODO
    def action_export_xlsx_handler(self):
        print("action_export_xlsx_handler")

    # TODO
    def action_import_xlm_handler(self):
        print("action_import_xlm_handler")

    # TODO
    def action_save_as_handler(self):
        print("action_save_as_handler")

    def refresh_table(self):
        for row_nr in range(0, self.PositonsTable.rowCount()):
            self.cell_changed_handler(row_nr, 5)

    # TODO
    def action_new_handler(self):
        print("action_new_handler")
        self.new_cost_estimate_window = new_cost_estimate()
        self.new_cost_estimate_window.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
