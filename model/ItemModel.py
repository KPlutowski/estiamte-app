from model.CheckBoxItem import CheckBoxItem
from model.DoubleSpinBoxItem import DoubleSpinBoxItem
from model.LineEditItem import LineEditItem
from model.Spreadsheet import Spreadsheet


class ItemModel:
    item_types = {
        "Pole numeryczne": DoubleSpinBoxItem,
        "Pole tekstowe": LineEditItem,
        "Pole wyboru": CheckBoxItem,
        "Arkusz kalkulacyjny": Spreadsheet
    }

    item_classes = {cls.__name__: cls for cls in item_types.values()}

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

    @staticmethod
    def get_class_from_name(class_name: str):
        return ItemModel.item_classes.get(class_name)

    @staticmethod
    def get_item_type_from_class(item_class):
        for key, cls in ItemModel.item_types.items():
            if cls == item_class:
                return key
        return None