import csv

import pandas as pd

from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QObject, pyqtSlot

from model.CheckBoxItem import CheckBoxItem
from model.DoubleSpinBoxItem import DoubleSpinBoxItem

from model.ItemWithFormula import ItemWithFormula
from model.LineEditItem import LineEditItem
from model.Model import Model
from model.Spreadsheet import Spreadsheet
from resources.TabWidget import GroupBox

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
                Model.find_item(name=sp_name).add_row()
            Model.find_item(name=sp_name).add_row()

        self.view.tabWidget.add_new_tab(constants.PROPERTIES_SPREADSHEET_NAME)

        self.view.tabWidget.add_new_tab(constants.POSITION_SPREADSHEET_NAME)
        self.view.tabWidget.add_new_tab(constants.ROOF_SPREADSHEET_NAME)
        self.view.tabWidget.add_new_tab(constants.FOUNDATION_SPREADSHEET_NAME)
        self.view.tabWidget.add_new_tab(constants.INSULATION_SPREADSHEET_NAME)

        self.view.tabWidget.get_tab_by_name(constants.POSITION_SPREADSHEET_NAME).add_property(constants.POSITION_SPREADSHEET_NAME, constants.POSITION_SPREADSHEET_NAME, Spreadsheet)
        self.view.tabWidget.get_tab_by_name(constants.ROOF_SPREADSHEET_NAME).add_property(constants.ROOF_SPREADSHEET_NAME, constants.ROOF_SPREADSHEET_NAME, Spreadsheet)
        self.view.tabWidget.get_tab_by_name(constants.FOUNDATION_SPREADSHEET_NAME).add_property(constants.FOUNDATION_SPREADSHEET_NAME, constants.FOUNDATION_SPREADSHEET_NAME, Spreadsheet)
        self.view.tabWidget.get_tab_by_name(constants.INSULATION_SPREADSHEET_NAME).add_property(constants.INSULATION_SPREADSHEET_NAME, constants.INSULATION_SPREADSHEET_NAME, Spreadsheet)

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
            property_tab.add_property(*c, i)

        load_default(constants.DEFAULT_POSITION_CSV_PATH, constants.POSITION_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_ROOF_CSV_PATH, constants.ROOF_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_FOUNDATION_CSV_PATH, constants.FOUNDATION_SPREADSHEET_NAME)
        load_default(constants.DEFAULT_INSULATION_CSV_PATH, constants.INSULATION_SPREADSHEET_NAME)

        Model.find_item("perimeter").set_item('=(PROPERTIES!buildingLength+PROPERTIES!buildingWidth)*2')
        Model.find_item("foundationArea").set_item('=PROPERTIES!buildingLength*PROPERTIES!buildingWidth')
        Model.find_item("rafterCount").set_item('=PROPERTIES!buildingLength/0.6')
        Model.find_item("rafterLength").set_item('=PROPERTIES!buildingWidth*0.9')
        Model.find_item("groundWallArea").set_item('=PROPERTIES!groundFloorHeight*PROPERTIES!perimeter')
        Model.find_item("kneeWallArea").set_item('=PROPERTIES!kneeWallHeight*PROPERTIES!perimeter')
        Model.find_item("gableArea").set_item('=PROPERTIES!buildingWidth*PROPERTIES!groundFloorHeight')
        Model.find_item("externalWallArea").set_item('=PROPERTIES!groundWallArea+PROPERTIES!kneeWallArea+PROPERTIES!gableArea')
        Model.find_item("eavesLenght").set_item('=IF(PROPERTIES!buildingWidth>6;0.80;0.60)')
        Model.find_item("spoutLength").set_item('=IF(PROPERTIES!buildingLength>7;0.8;0.6)')

    def setup_connections(self):
        # Tab widget
        self.view.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.view.tabWidget.propertyAdded.connect(self.new_GroupBox_setup_connections)

        # Formula_bar
        self.view.Formula_bar.textEdited.connect(self.formula_bar_edited)
        self.view.Formula_bar.editingFinished.connect(self.formula_bar_editing_finished)

        # File actions
        self.view.actionNew.triggered.connect(self.handle_new_file_action)
        self.view.actionOpen.triggered.connect(self.handle_file_open_action)
        self.view.actionSave.triggered.connect(self.handle_file_save_action)
        self.view.actionSaveAs.triggered.connect(self.handle_file_save_as_action)
        self.view.actionClose.triggered.connect(self.handle_file_close_action)

        # Export actions
        self.view.actionExportXlsx.triggered.connect(self.handle_export_xlsx_action)
        self.view.actionExportJson.triggered.connect(self.handle_export_json_action)
        self.view.actionExportPdf.triggered.connect(self.handle_export_pdf_action)

        # Import actions
        self.view.actionImportJson.triggered.connect(self.handle_import_json_action)

    def new_GroupBox_setup_connections(self, group_box: GroupBox):
        if isinstance(group_box.item, (DoubleSpinBoxItem, CheckBoxItem)):
            group_box.item.activeItemChangedSignal.connect(self.activeItemChanged)
        elif isinstance(group_box.item, LineEditItem):
            group_box.item.textEditedSignal.connect(self.itemWithFormulaTextEdited)
            group_box.item.doubleClickedSignal.connect(self.itemWithFormulaDoubleClicked)
            group_box.item.activeItemChangedSignal.connect(self.activeItemWithFormulaChanged)
        elif isinstance(group_box.item, Spreadsheet):
            group_box.item.textEditedSignal.connect(self.itemWithFormulaTextEdited)
            group_box.item.doubleClickedSignal.connect(self.itemWithFormulaDoubleClicked)
            group_box.item.activeItemChangedSignal.connect(self.activeItemWithFormulaChanged)

    ############################################

    def handle_new_file_action(self):
        from controlers.NewEstimateController import NewEstimateController
        self.new_estimate_cntroller = NewEstimateController(Model)

    def handle_file_open_action(self):
        print("handle_file_open_action")

    def handle_file_save_action(self):
        print("handle_file_save_action")

    def handle_file_save_as_action(self):
        print("handle_file_save_as_action")

    def handle_file_close_action(self):
        print("handle_file_close_action")

    def handle_export_xlsx_action(self):
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

    def handle_export_json_action(self):
        print("handle_export_json_action")

    def handle_export_pdf_action(self):
        print("handle_export_pdf_action")

    def handle_import_json_action(self):
        print("handle_import_json_action")

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

    ############################################

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
            for gb in tab.group_boxes:
                print(gb.name)
