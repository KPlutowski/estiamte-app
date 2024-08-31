import csv

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QModelIndex, QEvent, Qt, QMimeData
from PyQt6.QtGui import QMouseEvent, QDrag, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QMenu, QStyledItemDelegate, QVBoxLayout

from controlers.NewEstimateController import NewEstimateController
from model.CheckBoxItem import CheckBoxItem
from model.DoubleSpinnBoxItem import DoubleSpinnBoxItem
from model.GroupBox import MovableWidget
from model.ItemWithFormula import ItemWithFormula
from model.LineEditItem import LineEditItem
from model.Model import Model, Spreadsheet
from model.Spreadsheet import SpreadsheetCell
from resources.utils import letter_to_index
from views.MainView.MainView import MainView
import resources.constants as constants


class MainController(QObject):
    def __init__(self):
        super().__init__()

        self.view = MainView()
        self.setup_connections()
        self.default_data()



    def default_data(self):
        def load_default(csv_path, sp_name):
            line_count = 0
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    line_count += 1
                    # Calculate the NET_VALUE_COLUMN based on the formula
                    row[letter_to_index(constants.NET_VALUE_COLUMN[1])] = (
                        f'={sp_name}!'
                        f'{constants.QUANTITY_COLUMN[1]}{i + 1}*'
                        f'{sp_name}!'
                        f'{constants.PRICE_COLUMN[1]}{i + 1}'
                    )
                    for j, value in enumerate(row):
                        Model.get_cell(i, j, sp_name).set_item(value)

            Model.get_cell(line_count, letter_to_index(constants.PRICE_COLUMN[1]), sp_name).set_item(f'SUMA: ')
            Model.get_cell(line_count, letter_to_index(constants.NET_VALUE_COLUMN[1]), sp_name).set_item(
                f'=SUM({sp_name}!{constants.NET_VALUE_COLUMN[1]}1:{constants.NET_VALUE_COLUMN[1]}{line_count})')

        def add_lines(csv_path, sp_name):
            for _ in open(csv_path, encoding='utf-8'):
                Model.add_row(name=sp_name)
            Model.add_row(name=sp_name)

        add_lines(constants.DEFAULT_POSITION_CSV_PATH, constants.POSITION_SPREADSHEET_NAME)
        add_lines(constants.DEFAULT_ROOF_CSV_PATH, constants.ROOF_SPREADSHEET_NAME)
        add_lines(constants.DEFAULT_FOUNDATION_CSV_PATH, constants.FOUNDATION_SPREADSHEET_NAME)
        add_lines(constants.DEFAULT_INSULATION_CSV_PATH, constants.INSULATION_SPREADSHEET_NAME)

        load_default(constants.DEFAULT_POSITION_CSV_PATH, constants.POSITION_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_ROOF_CSV_PATH, constants.ROOF_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_FOUNDATION_CSV_PATH, constants.FOUNDATION_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_INSULATION_CSV_PATH, constants.INSULATION_SPREADSHEET_NAME)

        self.view.perimeter.set_item('=(PROPERTIES!buildingLength+PROPERTIES!buildingWidth)*2')
        self.view.foundationArea.set_item('=PROPERTIES!buildingLength*PROPERTIES!buildingWidth')
        self.view.rafterCount.set_item('=PROPERTIES!buildingLength/0.6')
        self.view.rafterLength.set_item('=PROPERTIES!buildingWidth*0.9')
        self.view.groundWallArea.set_item('=PROPERTIES!groundFloorHeight*PROPERTIES!perimeter')
        self.view.kneeWallArea.set_item('=PROPERTIES!kneeWallHeight*PROPERTIES!perimeter')
        self.view.gableArea.set_item('=PROPERTIES!buildingWidth*PROPERTIES!groundFloorHeight')
        self.view.externalWallArea.set_item('=PROPERTIES!groundWallArea+PROPERTIES!kneeWallArea+PROPERTIES!gableArea')
        self.view.eavesLenght.set_item('=IF(PROPERTIES!buildingWidth>6;0.80;0.60)')
        self.view.spoutLength.set_item('=IF(PROPERTIES!buildingLength>7;0.8;0.6)')

    def setup_connections(self):
        for spreadsheet in self.view.spreadsheets:
            spreadsheet.customContextMenuRequested.connect(self.spreadsheet_context_menu)
            spreadsheet.textEditedSignal.connect(self.itemWithFormulaTextEdited)
            spreadsheet.textEditingFinishedSignal.connect(self.itemWithFormulaTextEditedFinished)
            spreadsheet.doubleClickedSignal.connect(self.itemWithFormulaDoubleClicked)
            spreadsheet.activeItemChangedSignal.connect(self.activeItemWithFormulaChanged)

        for spin_box in self.view.spin_boxes:
            spin_box.activeItemChangedSignal.connect(self.activeItemChanged)

        for checkbox in self.view.checkboxes:
            checkbox.activeItemChangedSignal.connect(self.activeItemChanged)

        for line_edit in self.view.line_edits:
            line_edit.textEditedSignal.connect(self.itemWithFormulaTextEdited)
            line_edit.textEditingFinishedSignal.connect(self.itemWithFormulaTextEditedFinished)
            line_edit.doubleClickedSignal.connect(self.itemWithFormulaDoubleClicked)
            line_edit.activeItemChangedSignal.connect(self.activeItemWithFormulaChanged)

        # Tab widget
        self.view.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Formula_bar
        self.view.Formula_bar.textEdited.connect(self.formula_bar_edited)
        self.view.Formula_bar.editingFinished.connect(self.formula_bar_editing_finished)

        # Actions
        self.view.actionNew.triggered.connect(self.on_action_new_triggered)

    def itemWithFormulaTextEdited(self, item, edited_text):
        self.view.update_formula_bar(edited_text)

    def itemWithFormulaTextEditedFinished(self, item):
        if item is not None:
            item.set_item(self.view.Formula_bar.text())

    def itemWithFormulaDoubleClicked(self, item):
        item.setText(item.formula)
        self.view.update_formula_bar(item.formula)

    def activeItemWithFormulaChanged(self, item):
        if item is not None:
            Model.set_active_item(item)
            self.view.Formula_bar.setDisabled(False)
            self.view.update_formula_bar(item.formula)
            self.view.update_name_box(item.name)
            print(item)

    def activeItemChanged(self, item):
        if item is not None:
            Model.set_active_item(item)
            self.view.Formula_bar.setDisabled(True)
            self.view.update_formula_bar("")
            self.view.update_name_box(item.name)
            print(item)

    @pyqtSlot(str)
    def formula_bar_edited(self, text):
        if Model.get_active_item():
            if isinstance(Model.get_active_item(), ItemWithFormula):
                Model.get_active_item().value = text

    @pyqtSlot()
    def formula_bar_editing_finished(self):
        if Model.get_active_item():
            if isinstance(Model.get_active_item(), ItemWithFormula):
                Model.get_active_item().set_item(self.view.Formula_bar.text())

    def spreadsheet_context_menu(self, pos: QtCore.QPoint):
        widget = Model.get_active_item()

        if not isinstance(widget, SpreadsheetCell):
            return
        widget = widget.tableWidget()
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
        pass
