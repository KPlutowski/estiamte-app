import sys
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QTableWidget, QTreeWidget, QStyledItemDelegate, QMessageBox, QFileDialog, \
    QTableWidgetItem
from PyQt6 import QtCore, QtGui, QtWidgets
from main_window import Ui_MainWindow
from new_cost_estimate_window import Ui_new_cost_estimate_window
from enum import Enum


class row_type(Enum):
    position = "position"
    element = "element"
    root_element = "root_element"
    comment = "comment"


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        print('createEditor event fired')
        return


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


class basic_row:
    def __init__(self, _type: row_type):
        self.parent = None
        self.type = _type
        self.color = (0, 0, 0)
        self.bold = False
        self.children = []

        self.list_items: [QtWidgets.QTableWidgetItem] = [QtWidgets.QTableWidgetItem() for _ in range(8)]
        if _type == row_type.position:
            self.list_items[1].setText("P")
            self.list_items[2].setText("KNNR 1 0201-0200")
            self.list_items[3].setText("Roboty ziemne wykonywane koparkami przedsiębiernymi o pojemności łyżki 0,"
                                       "15 m3, z transportem urobku samochodami samowyładowczymi do 5 t na odległość "
                                       "do 1 km, grunt o normalnej wilgotności kat. III")
            self.list_items[4].setText("m3")
            self.list_items[5].setText("303")
            self.list_items[6].setText("5")
        elif _type == row_type.element:
            self.list_items[2].setText("1.")
            self.list_items[3].setText("STAN ZEROWY")
            self.list_items[4].setText("m3")
            self.list_items[5].setText("200")

            self.list_items[6].setFlags(self.list_items[6].flags() ^ QtCore.Qt.ItemFlag.ItemIsEditable)

            self.color = (0, 0, 255)
            self.bold = True
        elif _type == row_type.root_element:
            self.list_items[2].setText("Kosztorys")
            self.list_items[3].setText("Przykład - kosztorys szczegółowy")
            self.list_items[4].setText("m3")
            self.list_items[5].setText("600")
            for item in self.list_items:
                item.setFlags(item.flags() ^ QtCore.Qt.ItemFlag.ItemIsEditable)
            self.color = (255, 0, 0)
            self.bold = True
        elif _type == row_type.comment:
            self.list_items[1].setText("K")
            for column in (2, 4, 5, 6):
                self.list_items[column].setFlags(self.list_items[column].flags() ^ QtCore.Qt.ItemFlag.ItemIsEditable)
            self.bold = True
        self.reset_color()
        self.reset_bold()

    def reset_bold(self):
        font = QFont()
        font.setBold(self.bold)
        for item in self.list_items:
            item.setFont(font)

    def reset_color(self):
        for item in self.list_items:
            item.setForeground(QtGui.qRgb(self.color[0], self.color[1], self.color[2]))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.delegate = ReadOnlyDelegate(self)
        self.init_ui()
        ######################################
        self.csv_file = ""

        self.refresh_table()

    # TODO
    def action_new_handler(self):
        print("action_new_handler")
        self.new_cost_estimate_window = new_cost_estimate()
        self.new_cost_estimate_window.show()

    def init_ui(self):
        self.setupUi(self)
        self.PositonsTable.cellChanged.connect(self.cell_changed_handler)

        self.PositonsTable.customContextMenuRequested.connect(self.on_context_menu)
        self.PositonsTable.horizontalHeader().sectionResized.connect(self.PositonsTable.resizeRowsToContents)
        self.PositonsTable.setRowCount(0)
        self.PositonsTable.setColumnWidth(3, 400)

        # self.PositonsTable.setItemDelegateForColumn(0, self.delegate)
        # self.PositonsTable.setItemDelegateForColumn(1, self.delegate)
        # self.PositonsTable.setItemDelegateForColumn(7, self.delegate)

        self.actionNew.triggered.connect(self.action_new_handler)
        self.actionOpen.triggered.connect(self.action_open_handler)
        self.actionSave.triggered.connect(self.action_save_handler)
        self.actionClose.triggered.connect(self.action_close_handler)
        self.actionExport_xlsx.triggered.connect(self.action_export_xlsx_handler)
        self.actionImport_xlm.triggered.connect(self.action_import_xlm_handler)
        self.actionSave_as.triggered.connect(self.action_save_as_handler)
        self.actionImportCsv.triggered.connect(self.action_import_csv_handler)
        self.actionExportCsv.triggered.connect(self.action_export_csv_handler)

    def action_import_csv_handler(self):
        self.open_file()

    def action_export_csv_handler(self):
        self.save_file()

    def on_context_menu(self, pos):
        index = self.PositonsTable.indexAt(pos)
        valid_column = index.isValid() and index.column() == 1
        #  if you need to get the menu for that column, no matter if a row exists
        if not valid_column:
            left = self.PositonsTable.horizontalHeader().sectionPosition(1)
            width = self.PositonsTable.horizontalHeader().sectionSize(1)
            if left <= pos.x() <= left + width:
                valid_column = True
        if valid_column:
            menu = QtWidgets.QMenu()
            add_position = menu.addAction('Dopisz pozycję')
            add_element = menu.addAction('Dopisz Element')
            add_comment = menu.addAction('Dopisz komentarz')
            menu.addSeparator()

            cut = menu.addAction('Wytnij')
            copy = menu.addAction('Kopiuj')
            paste = menu.addAction('Wklej')

            delete = menu.addAction('Usuń...')
            action = menu.exec(self.PositonsTable.mapToGlobal(pos))

            if action == add_position:
                self.add_row(row_type.position)
            elif action == add_element:
                self.add_row(row_type.element)
            elif action == add_comment:
                self.add_row(row_type.comment)
            elif action == delete:
                self.delete_row()

            # elif action == cut:
            #     self.cut_row()
            # elif action == copy:
            #     self.copy_row()
            # elif action == paste:
            #     self.paste_row()

    def add_row(self, _type: row_type, row_position=-1):
        if row_position == -1:
            row_position = self.PositonsTable.currentRow() + 1
        self.PositonsTable.insertRow(row_position)
        row_to_add = basic_row(_type)
        for column in range(0, self.PositonsTable.columnCount()):
            self.PositonsTable.setItem(row_position, column, row_to_add.list_items[column])

        if _type == row_type.element:
            self.root.children.append(row_to_add)
        else:
            suma = 1  # because of root
            for el in self.root.children:
                suma = suma + len(el.children) + 1
                if suma >= row_position:
                    el.children.append(row_to_add)
                    break

    def delete_row(self):
        if self.PositonsTable.rowCount() > 0:
            row_position = self.PositonsTable.currentRow()
            self.PositonsTable.removeRow(row_position)

    def cell_changed_handler(self, row, column):
        # todo: sprawdz czy nie tekst, zaokraglanie do 2 miejsc dodanie zł

        if column == 5 or column == 6:
            if self.PositonsTable.item(row, 5) and self.PositonsTable.item(row, 6):
                if is_float(self.PositonsTable.item(row, 5).text()) and is_float(
                        self.PositonsTable.item(row, 6).text()):
                    quantity = float(self.PositonsTable.item(row, 5).text())
                    price = float(self.PositonsTable.item(row, 6).text())
                    self.PositonsTable.item(row, 5).setForeground(QtGui.qRgb(0, 0, 0))
                    self.PositonsTable.item(row, 6).setForeground(QtGui.qRgb(0, 0, 0))
                    self.PositonsTable.setItem(row, 7, QtWidgets.QTableWidgetItem(str(quantity * price)))

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open file', '', "CSV Files (*.csv *.tsv *.txt);;All Files (*.*)")
        if file_name:
            self.csv_file = file_name
            self.load_csv(self.csv_file)
            self.statusbar.showMessage(f"{file_name} loaded")

    def load_csv(self, filename):
        csv_text = open(filename, "r",encoding="UTF-8").read()
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

    def save_csv(self, filename):
        row_text = ""
        for row in range(self.PositonsTable.rowCount() - 1):

            for column in range(self.PositonsTable.columnCount() - 1):
                cell_text = self.PositonsTable.item(row, column).text()
                row_text += f"{cell_text}\t"
            row_text = row_text.rstrip("\t")
            row_text += "\n"
        with open(filename, "w",encoding="UTF-8") as f:
            f.write(row_text)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == QtCore.Qt.Key.Key_C and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.copy_row()
        elif event.key() == QtCore.Qt.Key.Key_V and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            self.paste_row()

    def copy_row(self):
        current_row = self.PositonsTable.currentRow()
        self.PositonsTable.clearSelection()
        self.PositonsTable.selectRow(current_row)
        copied_cells = sorted(self.PositonsTable.selectedIndexes())
        copy_text = ''

        for c in copied_cells:
            if self.PositonsTable.item(c.row(), c.column()):
                copy_text += self.PositonsTable.item(c.row(), c.column()).text()
                if c.column() == self.PositonsTable.columnCount() - 1:
                    copy_text += '\n'
                else:
                    copy_text += '\t'
            else:
                copy_text += '\t'
        QApplication.clipboard().setText(copy_text)

    def paste_row(self):
        pass
        rows = QApplication.clipboard().text().split('\n')
        row = rows[0].split('\t')
        if len(row) == 0:
            return

        row_to_paste = self.PositonsTable.currentRow() + 1
        self.PositonsTable.clearSelection()
        self.PositonsTable.selectRow(row_to_paste - 1)
        self.add_row(row_type.position)

        for i, value in enumerate(row):
            item = QtWidgets.QTableWidgetItem(value)
            self.PositonsTable.setItem(row_to_paste, i, item)

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
            self.cell_changed_handler(row_nr,5)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
