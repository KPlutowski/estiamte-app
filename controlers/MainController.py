import csv
from typing import Dict, Any

import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QMenu, QFileDialog
from PyQt6.QtCore import QObject, pyqtSlot, Qt

from model.CheckBoxItem import CheckBoxItem
from model.DoubleSpinBoxItem import DoubleSpinBoxItem

from model.ItemWithFormula import ItemWithFormula
from model.LineEditItem import LineEditItem
from model.Model import Model, Spreadsheet, db

from resources.TabWidget import MyTab, TabWidget, GroupBox
from resources.utils import letter_to_index
from views.MainView.MainView import MainView
import resources.constants as constants


class MainController(QObject):
    def __init__(self):
        super().__init__()
        self.view = MainView()
        self.setup_connections()
        self.default_data()
        self.properties = pd.DataFrame(columns=["WidgetName", "Value"])  # Initialize the DataFrame

    ############################################

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
                Model.find_spreadsheet(name=sp_name).add_row()
            Model.find_spreadsheet(name=sp_name).add_row()

        self.add_new_tab(constants.PROPERTIES_SPREADSHEET_NAME, self.view.tabWidget)

        self.add_new_tab(constants.POSITION_SPREADSHEET_NAME, self.view.tabWidget)
        self.add_new_tab(constants.ROOF_SPREADSHEET_NAME, self.view.tabWidget)
        self.add_new_tab(constants.FOUNDATION_SPREADSHEET_NAME, self.view.tabWidget)
        self.add_new_tab(constants.INSULATION_SPREADSHEET_NAME, self.view.tabWidget)

        self.add_property(constants.POSITION_SPREADSHEET_NAME, constants.POSITION_SPREADSHEET_NAME, Spreadsheet, Model.find_tab(constants.POSITION_SPREADSHEET_NAME))
        self.add_property(constants.ROOF_SPREADSHEET_NAME, constants.ROOF_SPREADSHEET_NAME, Spreadsheet, Model.find_tab(constants.ROOF_SPREADSHEET_NAME))
        self.add_property(constants.FOUNDATION_SPREADSHEET_NAME, constants.FOUNDATION_SPREADSHEET_NAME, Spreadsheet, Model.find_tab(constants.FOUNDATION_SPREADSHEET_NAME))
        self.add_property(constants.INSULATION_SPREADSHEET_NAME, constants.INSULATION_SPREADSHEET_NAME, Spreadsheet, Model.find_tab(constants.INSULATION_SPREADSHEET_NAME))

        add_lines(constants.DEFAULT_POSITION_CSV_PATH, constants.POSITION_SPREADSHEET_NAME)
        add_lines(constants.DEFAULT_ROOF_CSV_PATH, constants.ROOF_SPREADSHEET_NAME)
        add_lines(constants.DEFAULT_FOUNDATION_CSV_PATH, constants.FOUNDATION_SPREADSHEET_NAME)
        add_lines(constants.DEFAULT_INSULATION_CSV_PATH, constants.INSULATION_SPREADSHEET_NAME)

        property_tab = Model.find_tab(constants.PROPERTIES_SPREADSHEET_NAME)
        DEAFULT_PROPERTIES = [
            ("Powierzchnia siatki", "gridArea", DoubleSpinBoxItem),
            ("Długość budynku [m]", "buildingLength", DoubleSpinBoxItem),
            ("Szerokość budynku [m]", "buildingWidth", DoubleSpinBoxItem),
            ("Ilość szklanek", "glassQuantity", DoubleSpinBoxItem),
            ("Ścianki działowe na parterze [mb]", "groundFloorWalls", DoubleSpinBoxItem),
            ("Długość połaci", "roofLength", DoubleSpinBoxItem),
            ("Ścianki działowe na piętrze [mb]", "firstFloorWalls", DoubleSpinBoxItem),
            ("Wysokość ścianki kolankowej", "kneeWallHeight", DoubleSpinBoxItem),
            ("Wysokość ścian parteru", "groundFloorHeight", DoubleSpinBoxItem),

            ("Czy dom powyżej 70m2?", "largeHouse", CheckBoxItem),
            ("Czy poddasze użytkowe?", "attic", CheckBoxItem),
            ("Czy komin?", "chimney", CheckBoxItem),

            ("Obwód", "perimeter", LineEditItem),
            ("Powierzchnia Fundamentu", "foundationArea", LineEditItem),
            ("Powierzchnia ściany parteru [m2]", "groundWallArea", LineEditItem),
            ("Ilość krokwii", "rafterCount", LineEditItem),
            ("Powierzchnia ściany kolankowej [m2]", "kneeWallArea", LineEditItem),
            ("Powierzchnia szczytów [m2]", "gableArea", LineEditItem),
            ("Długość okapu", "eavesLenght", LineEditItem),
            ("Długość wypustu", "spoutLength", LineEditItem),
            ("Długość Krokwii", "rafterLength", LineEditItem),
            ("Powierzchnia ścian zewnętrznych [m2]", "externalWallArea", LineEditItem)
        ]
        for i, c in enumerate(DEAFULT_PROPERTIES):
            self.add_property(*c, property_tab, i)

        load_default(constants.DEFAULT_POSITION_CSV_PATH, constants.POSITION_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_ROOF_CSV_PATH, constants.ROOF_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_FOUNDATION_CSV_PATH, constants.FOUNDATION_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_INSULATION_CSV_PATH, constants.INSULATION_SPREADSHEET_NAME)

        Model.find_by_name("perimeter").set_item('=(PROPERTIES!buildingLength+PROPERTIES!buildingWidth)*2')
        Model.find_by_name("foundationArea").set_item('=PROPERTIES!buildingLength*PROPERTIES!buildingWidth')
        Model.find_by_name("rafterCount").set_item('=PROPERTIES!buildingLength/0.6')
        Model.find_by_name("rafterLength").set_item('=PROPERTIES!buildingWidth*0.9')
        Model.find_by_name("groundWallArea").set_item('=PROPERTIES!groundFloorHeight*PROPERTIES!perimeter')
        Model.find_by_name("kneeWallArea").set_item('=PROPERTIES!kneeWallHeight*PROPERTIES!perimeter')
        Model.find_by_name("gableArea").set_item('=PROPERTIES!buildingWidth*PROPERTIES!groundFloorHeight')
        Model.find_by_name("externalWallArea").set_item('=PROPERTIES!groundWallArea+PROPERTIES!kneeWallArea+PROPERTIES!gableArea')
        Model.find_by_name("eavesLenght").set_item('=IF(PROPERTIES!buildingWidth>6;0.80;0.60)')
        Model.find_by_name("spoutLength").set_item('=IF(PROPERTIES!buildingLength>7;0.8;0.6)')

    def setup_connections(self):
        # Tab widget
        self.view.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.view.tabWidget.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.tabWidget.tabBar().customContextMenuRequested.connect(self.tabWidget_context_menu)

        # Formula_bar
        self.view.Formula_bar.textEdited.connect(self.formula_bar_edited)
        self.view.Formula_bar.editingFinished.connect(self.formula_bar_editing_finished)

        # Actions
        self.view.actionNew.triggered.connect(self.on_action_new_triggered)
        self.view.actionExport_xlsx.triggered.connect(self.action_export_xlsx_handler)

    ############################################

    def action_export_xlsx_handler(self):
        def gather_data():
            """Gather properties and spreadsheets from the group boxes."""
            properties = {}
            sheets = {}
            for group_box in Model.list_all_group_boxes():
                if isinstance(group_box.item, Spreadsheet):
                    sheets[group_box.label.text()] = group_box.item
                elif isinstance(group_box.item, CheckBoxItem):
                    if group_box.item.isChecked():
                        properties[group_box.label.text()] = 'TAK'
                    else:
                        properties[group_box.label.text()] = 'NIE'
                else:
                    properties[group_box.label.text()] = group_box.item.value
            return properties, sheets

        def format_properties_sheet(worksheet, workbook):
            """ Format the properties worksheet. """
            right_format = workbook.add_format({
                'align': 'right', 'valign': 'vcenter', 'bold': True, 'border': 1, 'num_format': '#,##0.00'
            })
            yellow_format = workbook.add_format({
                'bg_color': 'yellow', 'align': 'right', 'valign': 'vcenter', 'bold': True, 'border': 1
            })

            # Apply formatting to the properties
            for row in range(len(self.properties)):
                widget_name = self.properties.iloc[row, 0]
                value = self.properties.iloc[row, 1]
                worksheet.write(row, 0, widget_name, yellow_format)
                worksheet.write(row, 1, value, right_format)

            # Set column widths for better readability
            worksheet.set_column('A:A', 17)
            worksheet.set_column('B:B', 10)

        def write_sheets(writer, sheets):
            """Write each spreadsheet to a new sheet."""
            for sheet_name, spreadsheet in sheets.items():
                df = spreadsheet.to_dataframe()

                df.to_excel(writer, sheet_name=sheet_name, index=False)
                sheet = writer.sheets[sheet_name]

                for col_num, col_data in enumerate(df.columns):
                    max_length = max(df[col_data].astype(str).map(len).max(), len(col_data))
                    sheet.set_column(col_num, col_num, max_length + 2)  # Adding padding for readability

        def save_to_excel(file_path, properties, sheets):
            """Save the properties and spreadsheets to an Excel file."""
            try:
                writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

                for label, value in properties.items():
                    self.properties = pd.concat([self.properties,pd.DataFrame([[label, value]], columns=["WidgetName", "Value"])], ignore_index=True)

                self.properties.to_excel(writer, index=False, header=False, sheet_name='Właściwości')
                format_properties_sheet(writer.sheets['Właściwości'], writer.book)

                # Write the spreadsheets to their respective sheets
                write_sheets(writer, sheets)

                # Save the Excel file
                writer._save()
            except Exception as e:
                print(f"Failed to save to Excel: {e}")

        try:
            file_path, _ = QFileDialog.getSaveFileName(self.view, "Save Excel File", "",
                                                       "Excel Files (*.xlsx);;All Files (*)")
            if not file_path:
                return

            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'

            properties, sheets = gather_data()
            save_to_excel(file_path, properties, sheets)
        except Exception as e:
            print(f"An error occurred during export: {e}")

    def on_action_new_triggered(self):
        from controlers.NewEstimateController import NewEstimateController
        self.new_estimate_cntroller = NewEstimateController(Model)

    def on_action_new_property(self, widget: MyTab, index: int):
        from controlers.NewPropertyFormController import NewPropertyController
        self.controller = NewPropertyController(widget, index)
        self.controller.property_added.connect(self.add_property)

    ############################################

    def itemWithFormulaTextEdited(self, item, edited_text):
        self.view.update_formula_bar(edited_text)

    def itemWithFormulaDoubleClicked(self, item):
        if item is not None:
            item.setText(item.formula)
            self.view.update_formula_bar(item.formula)

    def activeItemWithFormulaChanged(self, item):
        if item is not None:
            Model.set_active_item(item)
            self.view.Formula_bar.setDisabled(False)
            self.view.update_formula_bar(item.formula)
            self.view.update_name_box(item.name)
            print(item)
        else:
            Model.set_active_item(item)
            self.view.Formula_bar.setDisabled(True)
            self.view.update_formula_bar("")
            self.view.update_name_box("")

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

    @pyqtSlot(int)
    def on_tab_changed(self, index: int):
        name = self.view.tabWidget.widget(index).objectName()
        tab = Model.find_tab(name)
        if tab is not None:
            print(name)
            print(tab.group_boxes)

    ############################################

    def spreadsheet_context_menu(self, pos: QtCore.QPoint,spreadsheet: Spreadsheet):
        index = spreadsheet.indexAt(pos)

        menu = QMenu()
        add_position_action = menu.addAction('Add Row')
        menu.addSeparator()
        delete_action = menu.addAction('Delete Row')

        action = menu.exec(spreadsheet.mapToGlobal(pos))
        if not action:
            return

        row = index.row()
        if action == add_position_action:
            spreadsheet.add_row(row + 1)
        elif action == delete_action:
            spreadsheet.remove_row(row)

    def tabWidget_context_menu(self, pos: QtCore.QPoint):
        global_pos = self.view.tabWidget.tabBar().mapToGlobal(pos)
        menu = QMenu()
        add_tab_action = menu.addAction('Dodaj nową karte')

        action = menu.exec(global_pos)
        if action == add_tab_action:
            self.add_new_tab("new_tab",self.view.tabWidget)

    def tab_context_menu(self, pos: QtCore.QPoint, tab: MyTab):
        menu = QMenu()
        add_new_property_action = menu.addAction('Dodaj właściwość')
        delete_property_action = menu.addAction('Usuń właściwość')
        reset_spliter_action = menu.addAction('Przywróć domyślny układ')

        index = self.get_index(tab.mapToGlobal(pos))

        action = menu.exec(tab.mapToGlobal(pos))
        if action == add_new_property_action:
            self.on_action_new_property(tab, index)
        elif action == reset_spliter_action:
            tab.reset_spliter()
        elif action == delete_property_action:
            tab.delete_property(index)

    ############################################

    def add_new_tab(self, name: str, tab_widget: TabWidget):
        if name in db:
            raise KeyError(f"Tab found with name '{name}'.")
        my_tab = tab_widget.add_tab(name)

        my_tab.context_menu_request.connect(self.tab_context_menu)
        my_tab.installEventFilter(self)

        Model.add_tab_to_db(my_tab)

    def add_property(self, label_text: str, item_name: str, item_type, my_tab: MyTab, index: int = 0):
        if item_type is None:
            raise KeyError(f"Missing item_type.")
        tmp = GroupBox(label_text, item_name, item_type, my_tab)

        if isinstance(tmp.item, (DoubleSpinBoxItem, CheckBoxItem)):
            tmp.item.activeItemChangedSignal.connect(self.activeItemChanged)
        elif isinstance(tmp.item, LineEditItem):
            tmp.item.textEditedSignal.connect(self.itemWithFormulaTextEdited)
            tmp.item.doubleClickedSignal.connect(self.itemWithFormulaDoubleClicked)
            tmp.item.activeItemChangedSignal.connect(self.activeItemWithFormulaChanged)
        elif isinstance(tmp.item, Spreadsheet):
            tmp.item.context_menu_request.connect(self.spreadsheet_context_menu)
            tmp.item.textEditedSignal.connect(self.itemWithFormulaTextEdited)
            tmp.item.doubleClickedSignal.connect(self.itemWithFormulaDoubleClicked)
            tmp.item.activeItemChangedSignal.connect(self.activeItemWithFormulaChanged)
            for i, (header_name, _) in enumerate(constants.COLUMNS):
                item = QtWidgets.QTableWidgetItem()
                item.setText(header_name)
                tmp.item.setHorizontalHeaderItem(i, item)
        my_tab.add_group_box(tmp, index)

    ############################################

    def get_index(self, pos):
        current_widget = self.view.tabWidget.currentWidget()

        if not isinstance(current_widget, MyTab):
            return None

        closest_index = None
        min_distance = float('inf')  # Initialize with an infinite distance

        # Iterate through the widgets in the layout
        for i in range(current_widget.splitter.count()):
            widget = current_widget.splitter.widget(i)

            # Get the global coordinates of the widget's top-left and bottom-right corners
            top_left = widget.mapToGlobal(widget.rect().topLeft())
            bottom_right = widget.mapToGlobal(widget.rect().bottomRight())

            # Create a QRect representing the widget's global geometry
            widget_rect = QtCore.QRect(top_left, bottom_right)

            if widget_rect.contains(pos):
                # If the position is inside the widget, return its index immediately
                return i

            # Otherwise, calculate the distance from the click position to the widget's rect
            # Use the center of the widget for a more accurate "closeness" measure
            widget_center = widget_rect.center()
            distance = (pos - widget_center).manhattanLength()

            # Keep track of the widget with the minimum distance
            if distance < min_distance:
                min_distance = distance
                closest_index = i

        return closest_index
