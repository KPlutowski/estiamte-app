import csv
import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QMenu, QFileDialog
from PyQt6.QtCore import QObject, pyqtSlot, QEvent, Qt, QMimeData, QRect, QPoint
from PyQt6.QtGui import QDrag, QDragEnterEvent, QDropEvent, QMouseEvent

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
        self.data = pd.DataFrame(columns=["WidgetName", "Value"])  # Initialize the DataFrame

        self.eventTrap = None
        self.target = None
        self.dragged_widget = None
        self.view.setAcceptDrops(True)

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
                Model.get_spreadsheet_from_db(name=sp_name).add_row()
            Model.get_spreadsheet_from_db(name=sp_name).add_row()

        self.add_new_tab(constants.PROPERTIES_SPREADSHEET_NAME, self.view.tabWidget)

        self.add_new_tab(constants.POSITION_SPREADSHEET_NAME, self.view.tabWidget)
        self.add_new_tab(constants.ROOF_SPREADSHEET_NAME, self.view.tabWidget)
        self.add_new_tab(constants.FOUNDATION_SPREADSHEET_NAME, self.view.tabWidget)
        self.add_new_tab(constants.INSULATION_SPREADSHEET_NAME, self.view.tabWidget)

        self.add_property(constants.POSITION_SPREADSHEET_NAME,constants.POSITION_SPREADSHEET_NAME,Spreadsheet, Model.get_tab_from_db(constants.POSITION_SPREADSHEET_NAME))
        self.add_property(constants.ROOF_SPREADSHEET_NAME,constants.ROOF_SPREADSHEET_NAME,Spreadsheet, Model.get_tab_from_db(constants.ROOF_SPREADSHEET_NAME))
        self.add_property(constants.FOUNDATION_SPREADSHEET_NAME,constants.FOUNDATION_SPREADSHEET_NAME,Spreadsheet, Model.get_tab_from_db(constants.FOUNDATION_SPREADSHEET_NAME))
        self.add_property(constants.INSULATION_SPREADSHEET_NAME,constants.INSULATION_SPREADSHEET_NAME,Spreadsheet, Model.get_tab_from_db(constants.INSULATION_SPREADSHEET_NAME))

        add_lines(constants.DEFAULT_POSITION_CSV_PATH, constants.POSITION_SPREADSHEET_NAME)
        add_lines(constants.DEFAULT_ROOF_CSV_PATH, constants.ROOF_SPREADSHEET_NAME)
        add_lines(constants.DEFAULT_FOUNDATION_CSV_PATH, constants.FOUNDATION_SPREADSHEET_NAME)
        add_lines(constants.DEFAULT_INSULATION_CSV_PATH, constants.INSULATION_SPREADSHEET_NAME)

        property_tab = Model.get_tab_from_db(constants.PROPERTIES_SPREADSHEET_NAME)
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

        Model.get_from_db("perimeter").set_item('=(PROPERTIES!buildingLength+PROPERTIES!buildingWidth)*2')
        Model.get_from_db("foundationArea").set_item('=PROPERTIES!buildingLength*PROPERTIES!buildingWidth')
        Model.get_from_db("rafterCount").set_item('=PROPERTIES!buildingLength/0.6')
        Model.get_from_db("rafterLength").set_item('=PROPERTIES!buildingWidth*0.9')
        Model.get_from_db("groundWallArea").set_item('=PROPERTIES!groundFloorHeight*PROPERTIES!perimeter')
        Model.get_from_db("kneeWallArea").set_item('=PROPERTIES!kneeWallHeight*PROPERTIES!perimeter')
        Model.get_from_db("gableArea").set_item('=PROPERTIES!buildingWidth*PROPERTIES!groundFloorHeight')
        Model.get_from_db("externalWallArea").set_item('=PROPERTIES!groundWallArea+PROPERTIES!kneeWallArea+PROPERTIES!gableArea')
        Model.get_from_db("eavesLenght").set_item('=IF(PROPERTIES!buildingWidth>6;0.80;0.60)')
        Model.get_from_db("spoutLength").set_item('=IF(PROPERTIES!buildingLength>7;0.8;0.6)')

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

    def gather_properties_data(self):
        data = {}
        for obj in Model.get_items_from_db():
            if isinstance(obj,CheckBoxItem):
                if (obj.isChecked()):
                    data[obj.name] = 'TAK'
                else:
                    data[obj.name] = 'NIE'
            elif isinstance(obj,LineEditItem):
                data[obj.name] = obj.value
            elif isinstance(obj, DoubleSpinBoxItem):
                data[obj.name] = obj.value
        return data

    def action_export_xlsx_handler(self):
        print("action_export_xlsx_handler working")

        data = self.gather_properties_data()

        # Open a file dialog to choose the directory
        directory = QFileDialog.getExistingDirectory(self.view, "Select Directory")

        if directory:
            file_path = f"{directory}/output.xlsx"
            print(f"Selected directory: {directory}")

            sheets = {}
            for obj in Model.get_items_from_db():
                if isinstance(obj,Spreadsheet):
                    sheets[obj.name] = obj

            # Store the data in the DataFrame
            for name, value in data.items():
                self.data = pd.concat(
                    [self.data, pd.DataFrame([[name, value]], columns=["WidgetName", "Value"])],
                    ignore_index=True)

            writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
            self.data.to_excel(writer, index=False, header=False, sheet_name='Właściwości')

            for sheet_name, spreadsheet in sheets.items():
                df = spreadsheet.to_dataframe()
                df.to_excel(writer, sheet_name=sheet_name, index=False)

            workbook = writer.book
            worksheet = writer.sheets['Właściwości']
            worksheet.set_zoom(130)

            dct_Right = workbook.add_format({
                'align': 'right',  # Center alignment for both strings and numbers
                'valign': 'vcenter',  # Vertical alignment
                'bold': True,
                'border': 1,
                'num_format': '#,##0.00'
            })

            dct_Left = workbook.add_format({
                'align': 'left',  # Center alignment for both strings and numbers
                'valign': 'vcenter',  # Vertical alignment
                'bold': True,
                'border': 1
            })

            yellow_cell_format = workbook.add_format({
                'bg_color': 'yellow',
                'align': 'right',  # Center alignment for both strings and numbers
                'valign': 'vcenter',  # Vertical alignment
                'bold': True,
                'border': 1
            })

            red_cell_format = workbook.add_format({
                'bg_color': 'red',
                'align': 'right',  # Center alignment for both strings and numbers
                'valign': 'vcenter',  # Vertical alignment
                'bold': True,
                'border': 1
            })

            # Apply formats to columns
            for row in range(0, 9):
                # Read the current value of the cell
                cell_value = self.data.iloc[
                    row, 0]  # Assuming the data for column A is in the first column of DataFrame
                cell_value2 = self.data.iloc[row, 1]
                worksheet.write(row, 0, cell_value, yellow_cell_format)  # (row, col) is 0-indexed
                worksheet.write(row, 1, cell_value2, dct_Right)

            for row in range(9, 12):
                cell_value = self.data.iloc[
                    row, 0]  # Assuming the data for column A is in the first column of DataFrame
                cell_value2 = self.data.iloc[row, 1]
                worksheet.write(row, 0, cell_value, red_cell_format)  # (row, col) is 0-indexed
                worksheet.write(row, 1, cell_value2, dct_Left)

            for row in range(12, 22):
                # Read the current value of the cell
                cell_value = self.data.iloc[
                    row, 0]  # Assuming the data for column A is in the first column of DataFrame
                cell_value2 = self.data.iloc[row, 1]
                worksheet.write(row, 0, cell_value, yellow_cell_format)  # (row, col) is 0-indexed
                worksheet.write(row, 1, cell_value2, dct_Right)

            # Set column A and B to be wider
            worksheet.set_column('A:A', 17)
            worksheet.set_column('B:B', 10)

            # Format other sheets
            for sheet_name, spreadsheet in sheets.items():
                df = spreadsheet.to_dataframe()

                # Convert last 3 columns to decimal (float)
                if df.shape[1] >= 3:  # Check if there are at least 3 columns
                    last_three_cols = df.columns[-3:]
                    for col in last_three_cols:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)  # Use float

                # Write DataFrame to Excel
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Get the sheet and write "SUMA:" in the specified cell
                sheet = writer.sheets[sheet_name]

                # Calculate the target cell
                last_row = df.shape[0]  # The last row index
                target_col_suma = df.shape[1] - 2  # Second column from the last
                target_col_empty = df.shape[1] - 3  # Third column from the last
                target_cell_suma = xl_rowcol_to_cell(last_row, target_col_suma)
                target_cell_empty = xl_rowcol_to_cell(last_row, target_col_empty)

                # Create a format for right alignment
                right_align_format = workbook.add_format({
                    'align': 'right',
                    'valign': 'vcenter',
                    'bold': True
                })

                # Write "SUMA:" into the target cell with right alignment
                sheet.write(target_cell_suma, "SUMA:", right_align_format)
                sheet.write(target_cell_empty, "", right_align_format)

                # Apply decimal formatting to the last three columns
                if df.shape[1] >= 3:
                    last_three_cols = df.columns[-3:]
                    decimal_format = workbook.add_format({
                        'num_format': '0.00',
                        'align': 'right',
                        'valign': 'vcenter'
                    })
                    sheet = writer.sheets[sheet_name]
                    for col in last_three_cols:
                        col_idx = df.columns.get_loc(col)
                        sheet.set_column(col_idx, col_idx, None, decimal_format)

                # Auto-fit columns
                sheet = writer.sheets[sheet_name]
                for col_num, col_data in enumerate(df.columns):
                    max_length = max(df[col_data].astype(str).map(len).max(), len(col_data))
                    sheet.set_column(col_num, col_num, max_length + 2)  # Adding some padding

            writer._save()

        else:
            print("No directory selected.")

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
        pass

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

        index = self.get_index(tab.mapToGlobal(pos))

        action = menu.exec(tab.mapToGlobal(pos))
        if action == add_new_property_action:
            self.on_action_new_property(tab, index)

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
        tmp.drag_started.connect(self.on_drag_started)

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

    def on_drag_started(self, widget: GroupBox):
        self.view.tabWidget.dragged_widget = widget

    def get_index(self, pos):
        """Return the index of the widget under the given global position."""
        current_widget = self.view.tabWidget.currentWidget()

        if not isinstance(current_widget, MyTab):
            return None

        for i in range(current_widget.scroll_area_content.layout().count()):
            widget = current_widget.scroll_area_content.layout().itemAt(i).widget()

            top_left = widget.mapToGlobal(widget.rect().topLeft())
            bottom_right = widget.mapToGlobal(widget.rect().bottomRight())

            widget_rect = QtCore.QRect(top_left, bottom_right)

            if widget_rect.contains(pos):
                return i

        return None
