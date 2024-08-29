from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMainWindow, QTabWidget

from model.Model import Model, db
from model.Spreadsheet import Spreadsheet
from views.MainView.main_window_ui import Ui_MainWindow
import resources.constants as constants


class MainView(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.line_edits = [
            self.perimeter,
            self.foundationArea,
            self.rafterCount,
            self.rafterLength,
            self.groundWallArea,
            self.kneeWallArea,
            self.gableArea,
            self.externalWallArea,
            self.eavesLenght,
            self.spoutLength
        ]
        self.checkboxes = [
            self.attic,
            self.largeHouse,
            self.chimney
        ]
        self.spin_boxes = [
            self.gridArea,
            self.buildingLength,
            self.buildingWidth,
            self.glassQuantity,
            self.groundFloorWalls,
            self.roofLength,
            self.firstFloorWalls,
            self.kneeWallHeight,
            self.groundFloorHeight
        ]
        self.spreadsheets = []

        self.initUI()
        self.add_to_model()
        self.show()

    def make_spreadsheet(self, name: str, tab_widget: QTabWidget):
        def create_table_widget(parent_: QtWidgets.QWidget) -> QtWidgets.QTableWidget:
            table_widget = Spreadsheet(parent=parent_)
            table_widget.setObjectName(name)
            table_widget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            table_widget.setAlternatingRowColors(True)
            table_widget.setColumnCount(len(constants.COLUMNS))
            table_widget.horizontalHeader().setStretchLastSection(True)
            table_widget.setRowCount(0)
            return table_widget

        def set_column_headers(table_widget: QtWidgets.QTableWidget):
            for index, (header_name, _) in enumerate(constants.COLUMNS):
                item = QtWidgets.QTableWidgetItem()
                item.setText(header_name)
                table_widget.setHorizontalHeaderItem(index, item)

        if name in db:
            raise KeyError(f"Spreadsheet found with name '{name}'.")

        new_tab = QtWidgets.QWidget()
        new_tab.setObjectName(name)
        new_table_widget = create_table_widget(new_tab)

        vertical_layout = QtWidgets.QVBoxLayout(new_tab)
        vertical_layout.addWidget(new_table_widget)

        set_column_headers(new_table_widget)

        tab_widget.addTab(new_tab, name)
        self.spreadsheets.append(new_table_widget)

    def initUI(self):
        self.make_spreadsheet(constants.POSITION_SPREADSHEET_NAME, self.tabWidget)
        self.make_spreadsheet(constants.ROOF_SPREADSHEET_NAME, self.tabWidget)
        self.make_spreadsheet(constants.FOUNDATION_SPREADSHEET_NAME, self.tabWidget)
        self.make_spreadsheet(constants.INSULATION_SPREADSHEET_NAME, self.tabWidget)

    def add_to_model(self):
        for spreadsheet in self.spreadsheets:
            Model.add_item(spreadsheet)

        for spin_box in self.spin_boxes:
            Model.add_item(spin_box)

        for checkbox in self.checkboxes:
            Model.add_item(checkbox)

        for line_edit in self.line_edits:
            Model.add_item(line_edit)

    def update_formula_bar(self, value):
        self.Formula_bar.setText(f'{value}')

    def update_name_box(self, value):
        self.Name_box.setText(f'{value}')
