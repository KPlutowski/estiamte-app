from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QModelIndex, QEvent, Qt
from PyQt6.QtWidgets import QMenu, QStyledItemDelegate

from controlers.NewEstimateController import NewEstimateController
from model.Model import Model, Spreadsheet
from views.MainView.MainView import MainView
import resources.constants as constants


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
        self.view = MainView()
        self.delegate = ItemDelegate(self)
        self.setup_connections()
        self.default_data()
        Model.set_active_spreadsheet(self.view.tabWidget.tabText(self.view.tabWidget.currentIndex()))

    def default_data(self):
        Model.add_item(self.view.PositionsTableWidget)
        Model.add_item(self.view.PropertiesTableWidget)
        Model.add_item(self.view.spinn_box_ilosc)

        for i in constants.SPREADSHEET_PROPERTY_DEFAULTS:
            Model.add_row(text=i, name=constants.PROPERTY_TABLE_WIDGET_NAME)

        for i, row in enumerate(constants.SPREADSHEET_POSITIONS_DEFAULTS):
            row[5] = f'=Pozycje!D{i + 1}*Pozycje!E{i + 1}'
            Model.add_row(text=row, name=constants.POSITION_TABLE_WIDGET_NAME)

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
        self.view.Formula_bar.textEdited.connect(self.formula_bar_edited)

        # accept new formula
        self.delegate.commitData.connect(self.text_editing_finished)
        self.view.Formula_bar.editingFinished.connect(self.text_editing_finished)

        #Spinn Bob
        self.view.spinn_box_ilosc.textChanged.connect(self.view.spinn_box_ilosc.set_item)

    @pyqtSlot(str)
    def formula_bar_edited(self,text):
        if Model.get_active_spreadsheet():
            if Model.get_active_spreadsheet().currentItem():
                Model.get_active_spreadsheet().currentItem().setText(text)

    @pyqtSlot()
    def on_current_cell_changed(self):
        """Handle the event when the current cell changes."""
        item = Model.get_active_spreadsheet()
        if item is not None:
            item = item.currentItem()
            if item is not None:
                self.view.update_formula_bar(item.formula)
                self.view.update_name_box(item.name)
                print(item)
            else:
                pass
        else:
            self.view.update_formula_bar("")
            self.view.update_name_box("")

    @pyqtSlot(int, int)
    def on_cell_double_clicked(self, row: int, column: int):
        """Handle the event when a cell is double-clicked."""
        item = Model.get_active_spreadsheet().currentItem()
        item.setText(item.formula)
        self.view.update_formula_bar(item.formula)

    def text_editing_finished(self):
        """Handle the event when cell editing via delegate is finished."""
        if Model.get_active_spreadsheet():
            if Model.get_active_spreadsheet().currentItem():
                text = self.view.Formula_bar.text()
                Model.get_active_spreadsheet().currentItem().set_item(text)

    def show_context_menu(self, pos: QtCore.QPoint):
        widget = Model.get_active_spreadsheet()

        if not isinstance(widget, Spreadsheet):
            return
        index = widget.indexAt(pos)

        menu = QMenu()
        add_position_action = menu.addAction('Add Row')
        menu.addSeparator()
        delete_action = menu.addAction('Delete Row')

        action = menu.exec(widget.mapToGlobal(pos))
        if not action:
            return

        row = index.row()
        if action == add_position_action:
            Model.add_row(row + 1, name=widget.objectName())
        elif action == delete_action:
            Model.remove_row(row, name=widget.objectName())

    def on_action_new_triggered(self):
        self.new_estimate_cntr = NewEstimateController(Model)

    @pyqtSlot(int)
    def on_tab_changed(self, index: int):
        """Update active spreadsheet when tab is changed."""
        self.text_editing_finished()
        Model.set_active_spreadsheet(self.view.tabWidget.tabText(index))
        self.on_current_cell_changed()
