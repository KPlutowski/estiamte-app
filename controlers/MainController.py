import json
from typing import Optional

import pandas as pd

from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QObject, pyqtSlot

from model.CheckBoxItem import CheckBoxItem
from model.DoubleSpinBoxItem import DoubleSpinBoxItem
from model.ItemModel import ItemModel

from model.ItemWithFormula import ItemWithFormula
from model.LineEditItem import LineEditItem
from model.Model import Model
from model.Spreadsheet import Spreadsheet
from resources.TabWidget import GroupBox, MyTab

from resources.utils import parse_cell_reference
from views.MainView.MainView import MainView


class MainController(QObject):
    def __init__(self):
        super().__init__()
        self.view = MainView()

        self.current_file_path: Optional[str] = None
        self.is_edited: bool = False

        self.setup_connections()
        self.default_data()
        self.properties = pd.DataFrame(columns=["WidgetName", "Value"])  # Initialize the DataFrame

    ############################################

    def default_data(self):
        self.handle_file_open_action("resources/test.json")

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

    def handle_file_close_action(self):
        self.ask_for_save()
        self.view.close()

    def handle_export_xlsx_action(self):
        def gather_data():
            """Gather properties and spreadsheets from the group boxes."""
            properties = {}
            sheets = {}
            for tab in Model.get_list_of_tabs():
                for group_box in tab.group_boxes:
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
                    self.properties = pd.concat(
                        [self.properties, pd.DataFrame([[label, value]], columns=["WidgetName", "Value"])],
                        ignore_index=True)

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

    # TODO
    def handle_export_pdf_action(self):
        print("handle_export_pdf_action")

    def handle_file_open_action(self, file_path=None):
        """ IMPORT NEW FILE AND SET THE NEW PATH """
        if self.ask_for_save() == QMessageBox.StandardButton.Cancel:
            return

        if not file_path:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self.view, "Open project", "", "JSON Files (*.json)")

        self.reset_project()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                import_data = json.load(file)

            for tab_data in import_data:
                tab_name = tab_data['tab_name']
                tab = self.view.tabWidget.add_new_tab(tab_name)

                for group_box_data in tab_data['group_boxes']:
                    item_type = group_box_data['item_type']
                    item_name = group_box_data['item_name']
                    group_box_label = group_box_data['group_box_label']
                    group_box = tab.add_property(group_box_label, item_name, ItemModel.get_item_class(item_type))

                    if isinstance(group_box.item, Spreadsheet):
                        for i in range(group_box_data['row_count']):
                            group_box.item.add_row()
                        for cell_data in group_box_data['cells']:
                            sh_name, row, col = parse_cell_reference(cell_data['item_name'])
                            formula = cell_data.get('formula', '')
                            group_box.item.get_cell(row, col).set_item(formula)
                    else:
                        group_box.item.set_item(group_box_data.get('formula', ''))

            Model.recalculate()
            QMessageBox.information(self.view, "Open Successful", f"Data successfully opened from {file_path}")
        except Exception as e:
            QMessageBox.critical(self.view, "Open Failed", f"Failed to open data: {str(e)}")

        self.current_file_path = file_path
        self.is_edited = False

    def convert_to_json(self, data):
        try:
            return json.dumps(data, indent=4, ensure_ascii=False)
        except TypeError as e:
            QMessageBox.critical(self.view, "Export Failed", f"Failed to convert data to JSON: {str(e)}")
            return None

    def handle_file_save_action(self):
        """ Save file to json and set current_file_path to new path"""
        if self.is_edited:
            if self.current_file_path is None:
                file_dialog = QFileDialog()
                file_path, _ = file_dialog.getSaveFileName(self.view, "Save File Project", "", "JSON Files (*.json)")
                if file_path != '':
                    self.current_file_path = file_path
                else:
                    self.current_file_path = None

            if self.current_file_path:
                export_data = Model.get_dict_data()
                json_data = self.convert_to_json(export_data)
                if json_data:
                    try:
                        with open(self.current_file_path, 'w', encoding='utf-8') as file:
                            file.write(json_data)
                        QMessageBox.information(self.view, "Saving Successful",
                                                f"Data successfully saved to {self.current_file_path}")
                        self.is_edited = False
                        return 1
                    except Exception as e:
                        QMessageBox.critical(self.view, "Saving Failed", f"Failed to save data: {str(e)}")
                        self.current_file_path = None
        return QMessageBox.StandardButton.Cancel

    def reset_project(self):
        self.view.tabWidget.clean_up()
        self.properties = pd.DataFrame(columns=["WidgetName", "Value"])

        self.view.Formula_bar.clear()
        self.view.update_name_box("")
        self.view.tabWidget.setCurrentIndex(0)
        self.view.Formula_bar.setDisabled(True)

    def ask_for_save(self):
        if self.is_edited:
            reply = QMessageBox.question(self.view, "Unsaved Changes",
                                         "Do you want to save changes to the current project?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                                         QMessageBox.StandardButton.Cancel)

            if reply == QMessageBox.StandardButton.Yes:
                if self.handle_file_save_action() == QMessageBox.StandardButton.Cancel:
                    return QMessageBox.StandardButton.Cancel
            elif reply == QMessageBox.StandardButton.Cancel:
                return reply

    def handle_new_file_action(self):
        if self.ask_for_save() == QMessageBox.StandardButton.Cancel:
            return
        self.reset_project()
        self.current_file_path = None
        self.is_edited = False

    def handle_export_json_action(self):
        """ Save file to json and DOES NOT set current_file_path to new path"""

        def save_json_data_to_file(json_data):
            file_dialog = QFileDialog()
            file_name, _ = file_dialog.getSaveFileName(self.view, "Export to JSON", "", "JSON Files (*.json)")

            if file_name:
                try:
                    with open(file_name, 'w', encoding='utf-8') as file:
                        file.write(json_data)
                    QMessageBox.information(self.view, "Export Successful",
                                            f"Data successfully exported to {file_name}")
                except Exception as e:
                    QMessageBox.critical(self.view, "Export Failed", f"Failed to export data: {str(e)}")

        export_data = Model.get_dict_data()
        json_data = self.convert_to_json(export_data)

        if json_data:
            save_json_data_to_file(json_data)

    def handle_import_json_action(self, file_path=None):
        if self.ask_for_save() == QMessageBox.StandardButton.Cancel:
            return

        if not file_path:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self.view, "Import from JSON", "", "JSON Files (*.json)")

        self.reset_project()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                import_data = json.load(file)

            for tab_data in import_data:
                tab_name = tab_data['tab_name']
                tab = self.view.tabWidget.add_new_tab(tab_name)

                for group_box_data in tab_data['group_boxes']:
                    item_type = group_box_data['item_type']
                    item_name = group_box_data['item_name']
                    group_box_label = group_box_data['group_box_label']
                    group_box = tab.add_property(group_box_label, item_name, ItemModel.get_item_class(item_type))

                    if isinstance(group_box.item, Spreadsheet):
                        for i in range(group_box_data['row_count']):
                            group_box.item.add_row()
                        for cell_data in group_box_data['cells']:
                            sh_name, row, col = parse_cell_reference(cell_data['item_name'])
                            formula = cell_data.get('formula', '')
                            group_box.item.get_cell(row, col).set_item(formula)
                    else:
                        group_box.item.set_item(group_box_data.get('formula', ''))

            Model.recalculate()
            QMessageBox.information(self.view, "Import Successful", f"Data successfully imported from {file_path}")
        except Exception as e:
            QMessageBox.critical(self.view, "Import Failed", f"Failed to import data: {str(e)}")

        self.is_edited = True
        self.current_file_path = None

    ############################################

    def itemWithFormulaTextEdited(self, item, edited_text):
        self.view.update_formula_bar(edited_text)
        self.is_edited = True

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
                self.is_edited = True

    @pyqtSlot(int)
    def on_tab_changed(self, index: int):
        tab = self.view.tabWidget.widget(index)
        if tab is not None:
            print(tab.objectName())
            for gb in tab.group_boxes:
                print(gb.name)
