from PyQt6.QtCore import pyqtSignal, QObject

from model.ItemModel import ItemModel
from model.Model import Model
from resources.TabWidget import MyTab
from views.NewPropertyFormView.NewPropertyFormView import NewPropertyFormView


class NewPropertyController(QObject):
    property_added = pyqtSignal(str, str, object, MyTab, int)

    def __init__(self, widget: MyTab, index: int):
        super().__init__()
        self.model = ItemModel()
        self.view = NewPropertyFormView()
        self.widget = widget
        self.index = index if index is not None else 0

        self.setup_connections()

    def setup_connections(self):
        self.view.buttonBox.accepted.connect(self.handle_ok)
        self.view.buttonBox.rejected.connect(self.view.close)
        self.view.item_name_field.line_edit.textChanged.connect(self.clear_error)

    def handle_ok(self):
        item_name = self.view.item_name_field.text()
        label_text = self.view.label_text_LineEdit.text().strip()
        item_type = self.view.item_type_ComboBox.currentText()

        if not item_name:
            self.view.item_name_field.set_error("Item name cannot be empty.")
            return

        if Model.find_by_name(item_name) is not None:
            self.view.item_name_field.set_error("This item name already exists.")
            return

        if item_name:
            item_class = self.model.get_item_class(item_type)
            if item_class:
                self.property_added.emit(label_text, item_name, item_class, self.widget, self.index)
                self.view.close()

    def clear_error(self):
        self.view.item_name_field.clear_error()

    def close_window(self):
        self.view.close()
