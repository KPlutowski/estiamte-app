import csv

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QModelIndex, QEvent, Qt
from PyQt6.QtWidgets import QMenu, QStyledItemDelegate

from controlers.NewEstimateController import NewEstimateController
from model.Model import Model, Spreadsheet
from resources.utils import letter_to_index
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
        self.default_data()
        self.setup_connections()
        Model.set_active_spreadsheet(self.view.tabWidget.tabText(self.view.tabWidget.currentIndex()))

    def default_data(self):
        def load_default(csv_path, sp_name):
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    # Calculate the NET_VALUE_COLUMN based on the formula
                    row[letter_to_index(constants.NET_VALUE_COLUMN[1])] = (
                        f'={sp_name}!'
                        f'{constants.QUANTITY_COLUMN[1]}{i + 1}*'
                        f'{sp_name}!'
                        f'{constants.PRICE_COLUMN[1]}{i + 1}'
                    )
                    # Add the modified row to the spreadsheet
                    Model.add_row(text=row, name=sp_name)

        Model.add_spreadsheet(constants.POSITION_SPREADSHEET_NAME, self.view.tabWidget)
        Model.add_spreadsheet(constants.ROOF_SPREADSHEET_NAME, self.view.tabWidget)
        Model.add_spreadsheet(constants.FOUNDATION_SPREADSHEET_NAME, self.view.tabWidget)
        Model.add_spreadsheet(constants.INSULATION_SPREADSHEET_NAME, self.view.tabWidget)

        load_default(constants.DEFAULT_POSITION_CSV_PATH, constants.POSITION_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_ROOF_CSV_PATH, constants.ROOF_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_FOUNDATION_CSV_PATH, constants.FOUNDATION_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_INSULATION_CSV_PATH, constants.INSULATION_SPREADSHEET_NAME)

    def setup_connections(self):
        def set_spreadsheet_connections(tab):
            tab.setItemDelegate(self.delegate)
            tab.customContextMenuRequested.connect(self.show_context_menu)
            tab.cellDoubleClicked.connect(self.on_cell_double_clicked)
            tab.currentCellChanged.connect(self.on_current_cell_changed)

        # Tab widget
        self.view.tabWidget.currentChanged.connect(self.on_tab_changed)

        set_spreadsheet_connections(Model.get_spreadsheet(constants.POSITION_SPREADSHEET_NAME))
        set_spreadsheet_connections(Model.get_spreadsheet(constants.ROOF_SPREADSHEET_NAME))
        set_spreadsheet_connections(Model.get_spreadsheet(constants.FOUNDATION_SPREADSHEET_NAME))
        set_spreadsheet_connections(Model.get_spreadsheet(constants.INSULATION_SPREADSHEET_NAME))

        # Actions
        self.view.actionNew.triggered.connect(self.on_action_new_triggered)

        # real-time synchronization between formula bar and cell
        self.delegate.text_edited_signal.connect(self.view.update_formula_bar)
        self.view.Formula_bar.textEdited.connect(self.formula_bar_edited)

        # accept new formula
        self.delegate.commitData.connect(self.text_editing_finished)
        self.view.Formula_bar.editingFinished.connect(self.text_editing_finished)

        # SPIN BOX
        spin_boxes = [
            self.view.gridArea,
            self.view.buildingLength,
            self.view.buildingWidth,
            self.view.glassQuantity,
            self.view.groundFloorWalls,
            self.view.roofLength,
            self.view.kneeWallHeight,
            self.view.groundFloorHeight
        ]
        for spin_box in spin_boxes:
            Model.add_item(spin_box)
            spin_box.textChanged.connect(lambda text, sb=spin_box: sb.set_item(text))

        # CHECKBOX
        checkboxes = [
            self.view.attic,
            self.view.largeHouse,
            self.view.chimney
        ]
        for checkbox in checkboxes:
            Model.add_item(checkbox)
            checkbox.stateChanged.connect(lambda state, cb=checkbox: cb.set_item(state))

        # LINEEDIT
        line_edits = [
            self.view.perimeter,
            self.view.foundationArea,
            self.view.rafterCount,
            self.view.rafterLength,
            self.view.groundWallArea,
            self.view.kneeWallArea,
            self.view.gableArea,
            self.view.externalWallArea,
            self.view.eavesLenght,
            self.view.spoutLength
        ]
        for line_edit in line_edits:
            Model.add_item(line_edit)
            # line_edit.editingFinished.connect(lambda le=line_edit: le.set_item(le.text()))

    @pyqtSlot(str)
    def formula_bar_edited(self, text):
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
