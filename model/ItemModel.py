from model.CheckBoxItem import CheckBoxItem
from model.DoubleSpinBoxItem import DoubleSpinBoxItem
from model.LineEditItem import LineEditItem
from model.Spreadsheet import Spreadsheet


class ItemModel:
    item_types = {
        "DoubleSpinBox": DoubleSpinBoxItem,
        "LineEdit": LineEditItem,
        "CheckBox": CheckBoxItem,
        "Spreadsheet": Spreadsheet
    }

    @staticmethod
    def get_item_types():
        return list(ItemModel.item_types.keys())

    @staticmethod
    def get_item_class(item_type: str):
        return ItemModel.item_types.get(item_type)

    @staticmethod
    def get_all_item_classes():
        return list(ItemModel.item_types.values())

    @staticmethod
    def item_type_exists(item_type: str) -> bool:
        return item_type in ItemModel.item_types


