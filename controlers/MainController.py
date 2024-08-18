from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QModelIndex, QEvent, Qt
from PyQt6.QtWidgets import QMenu, QStyledItemDelegate, QLineEdit

from controlers.NewEstimateController import NewEstimateController
from model.Model import Model
from views.MainView.MainView import MainView


class ItemDelegate(QStyledItemDelegate):
    cellTextChanged = pyqtSignal(str)
    cellRevert = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = None

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QModelIndex) -> QtWidgets.QWidget:
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            self.editor = editor
            editor.textEdited.connect(self.on_editor_text_changed)
            editor.installEventFilter(self)
        return editor

    def on_editor_text_changed(self, text: str):
        self.cellTextChanged.emit(text)

    def revert_edit(self):
        self.cellRevert.emit()

    def eventFilter(self, obj: QtWidgets.QWidget, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self.revert_edit()
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
        self._model.add_spreadsheet(self.view.tabWidget.tabText(0), self.view.PositonsTableWidget)
        self._model.add_spreadsheet(self.view.tabWidget.tabText(1), self.view.PropertiesTableWidget)
        for name, spreadsheet in self._model.spreadsheets.items():
            for i in range(20):
                spreadsheet.add_row(i)
        self.on_tab_changed(self.view.tabWidget.currentIndex())

    def setup_connections(self):
        # Tab widget
        self.view.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Formula bar
        self.view.Formula_bar.editingFinished.connect(self.on_formula_bar_editing_finished)
        self.view.Formula_bar.textEdited.connect(self.on_formula_bar_text_edited)

        # Table Widgets
        self.view.PositonsTableWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.view.PropertiesTableWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.view.PositonsTableWidget.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.view.PropertiesTableWidget.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.view.PositonsTableWidget.currentCellChanged.connect(self.on_current_cell_changed)
        self.view.PropertiesTableWidget.currentCellChanged.connect(self.on_current_cell_changed)

        # Delegate
        self.delegate.cellTextChanged.connect(self.on_cell_text_changed)
        self.delegate.cellRevert.connect(self.on_cell_revert)
        self.delegate.closeEditor.connect(self.on_cell_editing_finished)
        self.view.PositonsTableWidget.setItemDelegate(self.delegate)
        self.view.PropertiesTableWidget.setItemDelegate(self.delegate)

        # Actions
        self.view.actionNew.triggered.connect(self.on_action_new_triggered)

    @pyqtSlot(int)
    def on_tab_changed(self, index: int):
        """Update active spreadsheet when tab is changed."""
        self.on_cell_editing_finished()
        tab_name = self.view.tabWidget.tabText(index)
        self._model.active_spreadsheet_name = tab_name

    @pyqtSlot(int, int)
    def on_current_cell_changed(self, row: int, column: int):
        """Handle the event when the current cell changes."""
        if self._model.active_spreadsheet and 0 <= row < self._model.active_spreadsheet.row_count:
            self._model.current_cell = self._model.get_cell(row, column, self._model.active_spreadsheet_name)
            cell = self._model.current_cell
            self.view.update_formula_bar(cell.formula)
            self.view.update_name_box(cell.name)
            self._model.original_text = cell.formula
            self._model.edited_text = cell.formula
            print(cell)

    @pyqtSlot(int, int)
    def on_cell_double_clicked(self, row: int, column: int):
        """Handle the event when a cell is double-clicked."""
        cell = self._model.current_cell
        cell.setText(cell.formula)
        self.view.update_formula_bar(cell.formula)
        self._model.original_text = cell.formula
        self._model.edited_text = cell.formula

    def on_formula_bar_text_edited(self, text: str):
        """Handle the event when the text in the formula bar is edited."""
        self._model.edited_text = text
        if self._model.current_cell:
            self._model.current_cell.setText(text)

    def on_formula_bar_editing_finished(self):
        """Handle the event when editing in the formula bar is finished."""
        self.on_cell_editing_finished()

    def on_cell_text_changed(self, text: str):
        """Handle the event when cell text is edited via delegate."""
        self._model.edited_text = text
        self.view.update_formula_bar(text)

    def on_cell_editing_finished(self):
        """Handle the event when cell editing via delegate is finished."""
        if self._model.current_cell:
            self._model.set_cell(self._model.current_row, self._model.current_column, self._model.edited_text,self._model.current_cell.sheet_name)
            self._model.original_text = self._model.edited_text

    def on_cell_revert(self):
        """Handle the event when cell editing is reverted."""
        if self._model.original_text != self._model.edited_text:
            self._model.edited_text = self._model.original_text
            self.view.update_formula_bar(self._model.edited_text)
            if self._model.current_cell:
                self._model.current_cell.setText(self._model.edited_text)

    def show_context_menu(self, pos: QtCore.QPoint):
        index = self.view.PositonsTableWidget.indexAt(pos) or self.view.PropertiesTableWidget.indexAt(pos)
        if not index.isValid():
            return

        menu = QMenu()
        add_position_action = menu.addAction('Add Row')
        menu.addSeparator()
        delete_action = menu.addAction('Delete Row')

        action = menu.exec(self.view.PositonsTableWidget.mapToGlobal(pos))
        if not action:
            return

        row = index.row()
        if action == add_position_action:
            self._model.active_spreadsheet.add_row(row + 1)
        elif action == delete_action:
            self._model.active_spreadsheet.remove_row(row)

    def on_action_new_triggered(self):
        self.new_estimate_cntr = NewEstimateController(self._model)

