from typing import List, Optional, Dict, Any

import pandas as pd
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal, QModelIndex, QEvent, Qt
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget, QStyledItemDelegate, QMenu

from model.ItemWithFormula import ItemWithFormula
from resources import constants
from resources.utils import index_to_letter, is_convertible_to_float


class ItemDelegate(QStyledItemDelegate):
    text_edited_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = None

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QModelIndex) -> QtWidgets.QWidget:
        self.editor = super().createEditor(parent, option, index)
        self.editor.installEventFilter(self)

        self.editor.textEdited.connect(self.text_edited_signal.emit)
        return self.editor

    def eventFilter(self, obj: QtWidgets.QWidget, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self.closeEditor.emit(self.editor)
            return True
        return super().eventFilter(obj, event)


class SpreadsheetCell(ItemWithFormula, QTableWidgetItem):
    def __init__(self, formula="", *args, **kwargs):
        super().__init__(formula, *args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{'-' * 80}\n"
            f"Cell at: row = {self.row()}, column = {self.column()}, Name: {self.name}\n"
            f"self: {hex(id(self))}\n"
            f"Value: {self.value}, Formula: {self.formula}\n"
            f"Format: {self.format}\n"
            f"Python_formula: {self.python_formula}\n"
            f"cells_that_i_dependents_on_and_names: {self.items_that_i_depend_on}\n"
            f"cells_that_dependents_on_me: {self.items_that_dependents_on_me}\n"
            f"Error Message: {self.error}\n"
            f"{'-' * 80}"
        )

    @property
    def name(self):
        return f"{self.tableWidget().objectName()}!{index_to_letter(self.column())}{self.row() + 1}"

    def set_display_text(self):
        self.setText(self.format.format_value(self._value))

    def get_dict_data(self) -> Dict[str, Any]:
        data = super().get_dict_data()
        data.pop('item_type')
        return data


class Spreadsheet(QTableWidget):
    doubleClickedSignal = pyqtSignal(object)
    textEditedSignal = pyqtSignal(object,str)
    textEditingFinishedSignal = pyqtSignal(object)
    activeItemChangedSignal = pyqtSignal(object)
    context_menu_request = pyqtSignal(QtCore.QPoint, object)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.worksheet: List[List[SpreadsheetCell]] = [[SpreadsheetCell() for _ in range(self.columnCount())] for _ in
                                                       range(0)]
        self.delegate = ItemDelegate(self)
        self.setItemDelegate(self.delegate)
        self.delegate.text_edited_signal.connect(self.text_edited)
        self.delegate.commitData.connect(self.editing_finished)
        self.currentCellChanged.connect(self.active_cell_changed)
        self.customContextMenuRequested.connect(self.context_menu)
        self.initUI()

    def clean_up(self):
        for i in range(self.rowCount()):
            self.remove_row(0)

    @property
    def name(self):
        return self.objectName()

    def initUI(self):
        self.setObjectName(self.name)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setAlternatingRowColors(True)
        self.setColumnCount(len(constants.COLUMNS))
        self.horizontalHeader().setStretchLastSection(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setRowCount(0)
        for i, (header_name, _) in enumerate(constants.COLUMNS):
            item = QtWidgets.QTableWidgetItem()
            item.setText(header_name)
            self.setHorizontalHeaderItem(i, item)

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

    def remove_row(self, index: int):
        if index < 0 or index >= self.rowCount():
            return

        cells_to_remove = self.worksheet[index]

        for cell_to_remove in cells_to_remove:
            for dependent in cell_to_remove.items_that_dependents_on_me:
                dependent.remove_dependent(cell_to_remove)

        for cell_to_remove in cells_to_remove:
            for name, dependent in cell_to_remove.items_that_i_depend_on.items():
                dependent.items_that_dependents_on_me.remove(cell_to_remove)

        self.worksheet.pop(index)
        self.removeRow(index)

    def get_cell(self, row, column):
        if 0 <= row < self.rowCount() and 0 <= column < self.columnCount():
            return self.worksheet[row][column]
        return None

    #Transforming into the DataFrame
    def to_dataframe(self) -> pd.DataFrame:
        data = []
        for row in self.worksheet:
            row_data = []
            for cell in row:
                row_data.append(float(cell.text()) if is_convertible_to_float(cell.text()) else cell.text())
            data.append(row_data)

        df = pd.DataFrame(data, columns=self.get_headers())
        return df

    def get_headers(self) -> List[str]:
        return [self.horizontalHeaderItem(col).text() if self.horizontalHeaderItem(col) else f'Column {col + 1}' for col in range(self.columnCount())]

    def recalculate(self):
        for row in self.worksheet:
            for cell in row:
                cell.recalculate()

    def get_dict_data(self) -> Dict[str, Any]:
        from model.ItemModel import ItemModel

        cells = []
        for row in self.worksheet:
            for cell in row:
                cells.append(cell.get_dict_data())
        data = {
            'cells': cells,
            'item_name': self.name,
            'row_count': self.rowCount(),
            'column_count': self.columnCount(),
            'item_type': ItemModel.get_item_type_from_class(type(self))
        }

        return data

    ###############################################

    def mouseDoubleClickEvent(self, event: QEvent):
        super().mouseDoubleClickEvent(event)
        self.doubleClickedSignal.emit(self.currentItem())

    def active_cell_changed(self):
        self.activeItemChangedSignal.emit(self.currentItem())

    def text_edited(self, text):
        self.textEditedSignal.emit(self.currentItem(), text)

    def editing_finished(self):
        self.currentItem().set_item(self.currentItem().text())

    def focusInEvent(self, event: QEvent):
        super().focusInEvent(event)
        self.activeItemChangedSignal.emit(self.currentItem())

    def context_menu(self, pos):
        index = self.indexAt(pos)

        menu = QMenu()
        add_position_action = menu.addAction('Dodaj wiersz')
        menu.addSeparator()
        delete_action = menu.addAction('Usuń wiersz')

        action = menu.exec(self.mapToGlobal(pos))
        if not action:
            return

        row = index.row()
        if action == add_position_action:
            self.add_row(row + 1)
        elif action == delete_action:
            self.remove_row(row)
