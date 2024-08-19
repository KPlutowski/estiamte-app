from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QModelIndex, QEvent, Qt
from PyQt6.QtWidgets import QMenu, QStyledItemDelegate, QLineEdit

from controlers.NewEstimateController import NewEstimateController
from model.Model import Model
from views.MainView.MainView import MainView


class ItemDelegate(QStyledItemDelegate):
    text_edited_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = None

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QModelIndex) -> QtWidgets.QWidget:
        self.editor = super().createEditor(parent, option, index)
        self.editor.installEventFilter(self)

        # connecting signals
        self.editor.textEdited.connect(self.text_edited_signal.emit)

        return self.editor

    def eventFilter(self, obj: QtWidgets.QWidget, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self.closeEditor.emit(self.editor)
            return True
        return super().eventFilter(obj, event)


class MainController(QObject):
    def __init__(self):
        super().__init__()
        self._model = Model()
        self.view = MainView()
        self.delegate = ItemDelegate(self)
        self.setup_connections()
        self.default_data()

    def default_data(self):
        for i, table in enumerate([self.view.PositionsTableWidget,self.view.PropertiesTableWidget]):
            self._model.add_spreadsheet(self.view.tabWidget.tabText(i), table)
            for _ in range(20):
                self._model.add_row()
        self.on_tab_changed(self.view.tabWidget.currentIndex())

    def setup_connections(self):
        # Tab widget
        self.view.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Table Widgets
        self.view.PositionsTableWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.view.PropertiesTableWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.view.PositionsTableWidget.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.view.PropertiesTableWidget.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.view.PositionsTableWidget.currentCellChanged.connect(self.on_current_cell_changed)
        self.view.PropertiesTableWidget.currentCellChanged.connect(self.on_current_cell_changed)
        self.view.PositionsTableWidget.setItemDelegate(self.delegate)
        self.view.PropertiesTableWidget.setItemDelegate(self.delegate)

        # Actions
        self.view.actionNew.triggered.connect(self.on_action_new_triggered)

        # real-time synchronization between formula bar and cell
        self.delegate.text_edited_signal.connect(self.view.update_formula_bar)
        self.view.Formula_bar.textEdited.connect(
            lambda text: self._model.current_cell.setText(text) if self._model.current_cell else None)

        # accept new formula
        self.delegate.commitData.connect(self.text_editing_finished)
        self.view.Formula_bar.editingFinished.connect(self.text_editing_finished)

    @pyqtSlot(int, int)
    def on_current_cell_changed(self, row: int, column: int):
        """Handle the event when the current cell changes."""
        if self._model.active_spreadsheet and 0 <= row < self._model.active_spreadsheet.row_count:
            self._model.current_cell = self._model.get_cell(row, column, self._model.active_spreadsheet.name)
            cell = self._model.current_cell
            self.view.update_formula_bar(cell.formula)
            self.view.update_name_box(cell.name)
            print(cell)

    @pyqtSlot(int, int)
    def on_cell_double_clicked(self, row: int, column: int):
        """Handle the event when a cell is double-clicked."""
        cell = self._model.current_cell
        cell.setText(cell.formula)
        self.view.update_formula_bar(cell.formula)

    def text_editing_finished(self):
        """Handle the event when cell editing via delegate is finished."""
        if self._model.current_cell:
            text = self.view.Formula_bar.text()
            self._model.set_cell(self._model.current_row, self._model.current_column, text, self._model.current_cell.sheet_name)

    def show_context_menu(self, pos: QtCore.QPoint):
        index = self.view.PositionsTableWidget.indexAt(pos) or self.view.PropertiesTableWidget.indexAt(pos)
        if not index.isValid():
            return

        menu = QMenu()
        add_position_action = menu.addAction('Add Row')
        menu.addSeparator()
        delete_action = menu.addAction('Delete Row')

        action = menu.exec(self.view.PositionsTableWidget.mapToGlobal(pos))
        if not action:
            return

        row = index.row()
        if action == add_position_action:
            self._model.active_spreadsheet.add_row(row + 1)
        elif action == delete_action:
            self._model.active_spreadsheet.remove_row(row)

    def on_action_new_triggered(self):
        self.new_estimate_cntr = NewEstimateController(self._model)

    @pyqtSlot(int)
    def on_tab_changed(self, index: int):
        """Update active spreadsheet when tab is changed."""
        self.text_editing_finished()
        tab_name = self.view.tabWidget.tabText(index)
        self._model.active_spreadsheet = tab_name