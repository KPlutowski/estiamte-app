from PyQt6 import QtCore
from PyQt6.QtWidgets import QLineEdit, QStyledItemDelegate
from PyQt6.QtCore import Qt, pyqtSignal, QModelIndex, QEvent

import sys
from PyQt6 import QtWidgets
from main_window import Ui_MainWindow
from Spreadsheet import SpreadsheetManager
from controller import Controller



class ItemDelegate(QStyledItemDelegate):
    cellTextChanged = pyqtSignal(str)
    cellRevert = pyqtSignal()

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QModelIndex) -> QtWidgets.QWidget:
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.textEdited.connect(lambda text: self.on_editor_text_changed(index, text))
            editor.installEventFilter(self)
        return editor

    def on_editor_text_changed(self, index: QModelIndex, text: str):
        self.cellTextChanged.emit(text)

    def revert_edit(self):
        self.cellRevert.emit()

    def eventFilter(self, obj: QtWidgets.QWidget, event: QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.revert_edit()
                return True
        return super().eventFilter(obj, event)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.spreadsheet_manager = SpreadsheetManager()
        self.delegate = ItemDelegate(self)
        self.controller = Controller(self, self.spreadsheet_manager)

        self.init_tables()

    def init_tables(self):
        self.spreadsheet_manager.add_spreadsheet(self.tabWidget.tabText(0), self.PositonsTableWidget)
        self.spreadsheet_manager.add_spreadsheet(self.tabWidget.tabText(1), self.PropertiesTableWidget)
        for name, spreadsheet in self.spreadsheet_manager.spreadsheets.items():
            table_widget = spreadsheet.table_widget
            table_widget.setItemDelegate(self.delegate)
            table_widget.cellDoubleClicked.connect(self.controller.handle_cell_double_click)
            table_widget.currentCellChanged.connect(self.controller.handle_current_cell_change)
            table_widget.customContextMenuRequested.connect(self.controller.show_context_menu)
            table_widget.horizontalHeader().sectionResized.connect(table_widget.resizeRowsToContents)
            table_widget.setRowCount(0)
            for i in range(20):
                spreadsheet.add_row(i)
        self.controller.tab_changed(self.tabWidget.currentIndex())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

