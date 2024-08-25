from typing import List, Optional, Dict, Set, Union
from collections import deque, defaultdict
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QWidget, QTabWidget

from model.Enums import ErrorType
from model.Item import Item
from model.ItemWithFormula import ItemWithFormula
from model.Spreadsheet import Spreadsheet, SpreadsheetCell
from resources import constants
from resources.utils import parse_cell_reference, parse_cell_range


class Model:
    __active_item = None

    @staticmethod
    def set_active_item(item):
        Model.__active_item = item

    @staticmethod
    def get_active_item() -> ItemWithFormula:
        return Model.__active_item

    @staticmethod
    def add_item(widget: QWidget):
        if widget.objectName() not in db:
            name = widget.objectName()
            db[name] = widget
        else:
            raise NameError(f'!!ERROR AT Model.add_item, name:{widget.objectName()}!!')

    @staticmethod
    def calculate_dirty_items():
        """Calculate and update the values of all dirty cells."""
        global dirty_items

        def topological_sort(cells: List[Item]) -> List[Item]:
            """Perform a topological sort of the cells based on their dependencies, excluding cells with errors."""
            # Filter out cells with errors
            cells = [cell for cell in cells if cell.error is None]

            if not cells:
                return []

            # Initialize in-degree count for each cell
            in_degree = defaultdict(int)
            for cell in cells:
                for dependent in cell.items_that_dependents_on_me:
                    if dependent in cells:
                        in_degree[dependent] += 1

            # Initialize queue with cells that have zero in-degree
            zero_in_degree = deque(cell for cell in cells if in_degree[cell] == 0)
            topological_order = []

            while zero_in_degree:
                cell = zero_in_degree.popleft()
                topological_order.append(cell)
                for dependent in cell.items_that_dependents_on_me:
                    if dependent in cells:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            zero_in_degree.append(dependent)

            if len(topological_order) != len(cells):
                raise RuntimeError("Cyclic dependency detected")
            return topological_order

        if not dirty_items:
            return
        non_error_cells = []

        # Detect circular dependencies
        for cell in dirty_items:
            for dependent in cell.items_that_dependents_on_me:
                if cell.check_circular_dependency(dependent):
                    cell.set_error(ErrorType.CIRCULAR)
                    cell.evaluate_formula()
            if cell.error is None:
                non_error_cells.append(cell)

        if non_error_cells:
            order = topological_sort(non_error_cells)
            for cell in order:
                if cell in dirty_items:
                    cell.evaluate_formula()
                    dirty_items.discard(cell)

        dirty_items = {cell for cell in dirty_items if not cell.error}
        assert not dirty_items, "Some cells are still marked as dirty after calculation."

    @staticmethod
    def remove_spreadsheet(name: str):
        """Remove the spreadsheet table with the given name."""
        if name not in db:
            raise KeyError(f"No spreadsheet found with name '{name}'.")
        del db[name]

    @staticmethod
    def add_spreadsheet(name: str, view: QTabWidget):
        def create_table_widget(name: str, parent_: QtWidgets.QWidget) -> QtWidgets.QTableWidget:
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
        new_table_widget = create_table_widget(name, new_tab)

        vertical_layout = QtWidgets.QVBoxLayout(new_tab)
        vertical_layout.addWidget(new_table_widget)

        set_column_headers(new_table_widget)

        view.addTab(new_tab, name)
        Model.add_item(new_table_widget)

    @staticmethod
    def get_spreadsheet(name) -> Spreadsheet:
        if name in db:
            if isinstance(db[name], Spreadsheet):
                return db[name]
        return None

    @staticmethod
    def add_row(index=None, text: Optional[List[str]] = None, name=None):
        if name in db:
            db[name].add_row(index, text)

    @staticmethod
    def remove_row(index=None, name=None):
        if name in db:
            db[name].remove_row(index)

    @staticmethod
    def get_cell(row_or_address: Union[int, str], column: Optional[int] = None,
                 name_of_spreadsheet: Optional[str] = None) -> Optional[SpreadsheetCell]:
        # If column is not None, it means we're using row and column parameters
        if column is not None and name_of_spreadsheet is not None:
            if name_of_spreadsheet in db:
                return db[name_of_spreadsheet].get_cell(row_or_address, column)

        # If column is None, we assume we're using the address format
        elif isinstance(row_or_address, str):
            sheet_name, row_number, col_number = parse_cell_reference(row_or_address)
            if sheet_name in db:
                if 0 <= row_number < db[sheet_name].rowCount():
                    if 0 <= col_number < db[sheet_name].columnCount():
                        return db[sheet_name].get_cell(row_number, col_number)
        return None

    @staticmethod
    def get_range(start_row_or_range: Union[int, str], start_col: Optional[int] = None,
                  end_row: Optional[int] = None, end_col: Optional[int] = None, sheet_name: Optional[str] = None) -> \
    List[SpreadsheetCell]:
        # If end_row and end_col are provided, assume we're using explicit start and end coordinates
        if end_row is not None and end_col is not None and sheet_name is not None:
            return [
                Model.get_cell(row, col, sheet_name)
                for row in range(start_row_or_range, end_row + 1)
                for col in range(start_col, end_col + 1)
            ]

        # If end_row and end_col are not provided, assume start_row_or_range is a range string
        elif isinstance(start_row_or_range, str):
            sheet_name, start_row, start_col, end_row, end_col = parse_cell_range(start_row_or_range)
            return [
                Model.get_cell(row, col, sheet_name)
                for row in range(start_row, end_row + 1)
                for col in range(start_col, end_col + 1)
            ]

        # Return an empty list if inputs are not valid
        return []

    @staticmethod
    def get_property(address: str):
        name = address[len('PROPERTIES!'):]
        if not name:
            return None
        return db.get(name)


dirty_items: Set[Item] = set()
db: Dict[str, any] = {}
