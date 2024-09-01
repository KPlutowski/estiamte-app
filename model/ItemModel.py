from model.CheckBoxItem import CheckBoxItem
from model.DoubleSpinnBoxItem import DoubleSpinnBoxItem
from model.LineEditItem import LineEditItem
from model.Spreadsheet import Spreadsheet


class ItemModel:
    def __init__(self):
        self.item_types = {
            "DoubleSpinnBox": DoubleSpinnBoxItem,
            "LineEdit": LineEditItem,
            "CheckBox": CheckBoxItem,
            "Spreadsheet": Spreadsheet
        }

    def get_item_types(self):
        return list(self.item_types.keys())

    def get_item_class(self, item_type: str):
        return self.item_types.get(item_type)
