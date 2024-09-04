from typing import List, Optional, Dict, Set, Union, Any
from collections import deque, defaultdict

from model.Enums import ErrorType
from model.Item import Item
from model.ItemWithFormula import ItemWithFormula
from model.Spreadsheet import Spreadsheet, SpreadsheetCell
from resources.TabWidget import MyTab, TabWidget, GroupBox
from resources.utils import parse_cell_reference, parse_cell_range, is_convertible_to_float


class Model:
    __active_item = None

    @staticmethod
    def set_active_item(item):
        Model.__active_item = item

    @staticmethod
    def get_active_item() -> ItemWithFormula:
        return Model.__active_item

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
    def get_cell(row_or_address: Union[int, str], column: Optional[int] = None,
                 name_of_spreadsheet: Optional[str] = None) -> Optional[SpreadsheetCell]:
        # If column is not None, it means we're using row and column parameters
        if column is not None and name_of_spreadsheet is not None:
            if name_of_spreadsheet in db:
                return Model.find_spreadsheet(name_of_spreadsheet).get_cell(row_or_address, column)

        # If column is None, we assume we're using the address format
        elif isinstance(row_or_address, str):
            sheet_name, row_number, col_number = parse_cell_reference(row_or_address)
            return Model.find_spreadsheet(sheet_name).get_cell(row_number, col_number)
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
        return Model.find_by_name(name)

    @staticmethod
    def evaluate_formula(formula: str) -> str:
        return str(eval(formula))
    #########################################

    @staticmethod
    def sum_function(cells: List['SpreadsheetCell']) -> float:
        """Sum the values of a list of cells."""
        total = 0.0
        for cell in cells:
            if is_convertible_to_float(cell.value):
                total += float(cell.value)
            else:
                # Handle non-numeric values if needed
                pass
        return total

    @staticmethod
    def if_function(logical_test, value_if_true, value_if_false):
        if logical_test:
            return value_if_true
        else:
            return value_if_false

    #########################################

    @staticmethod
    def add_tab_to_db(item: MyTab) -> None:
        if item.name in db:
            raise NameError(f'TabWidget found with name {item.name}')
        db[item.name] = item

    @staticmethod
    def find_tab(name: str) -> Optional[MyTab]:
        return db.get(name)

    @staticmethod
    def list_all_tabs() -> list[MyTab]:
        return list(db.values())

    @staticmethod
    def find_item(name: str) -> Optional[Item]:
        for tab in db.values():
            for group_box in tab.group_boxes.values():
                if group_box.item.name == name:
                    return group_box.item
        return None

    @staticmethod
    def find_spreadsheet(name: str) -> Optional[Spreadsheet]:
        for tab in db.values():
            for group_box in tab.group_boxes.values():
                if group_box.item.name == name and isinstance(group_box.item, Spreadsheet):
                    return group_box.item
        return None

    @staticmethod
    def list_all_items() -> list[Any]:
        return [group_box.item for tab in db.values() for group_box in tab.group_boxes.values()]

    @staticmethod
    def find_by_name(name: str) -> Optional[Union[MyTab, GroupBox, Item]]:
        for tab in db.values():
            if tab.name == name:
                return tab
            for group_box in tab.group_boxes.values():
                if group_box.name == name or group_box.item.name == name:
                    return group_box if group_box.name == name else group_box.item
        return None

    @staticmethod
    def remove_tab(name: str) -> Optional[MyTab]:
        return db.pop(name, None)

    @staticmethod
    def remove_item(name: str) -> Optional[GroupBox]:
        for tab in db.values():
            group_box = tab.group_boxes.pop(name, None)
            if group_box:
                return group_box
        return None

    @staticmethod
    def update_tab(name: str, updated_tab: MyTab) -> None:
        if name not in db:
            raise KeyError(f'TabWidget with name {name} not found')
        db[name] = updated_tab

    @staticmethod
    def update_item(tab_name: str, item_name: str, updated_item: Item) -> None:
        tab = db.get(tab_name)
        if tab:
            for group_box in tab.group_boxes.values():
                if group_box.item.name == item_name:
                    group_box.item = updated_item
                    return
        raise KeyError(f'Item with name {item_name} not found in tab {tab_name}')


dirty_items: Set[Item] = set()
db: Dict[str, MyTab] = {}
