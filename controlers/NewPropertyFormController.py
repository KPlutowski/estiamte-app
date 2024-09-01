from PyQt6.QtCore import pyqtSignal, QObject

from model.ItemModel import ItemModel
from resources.TabWidget import PropertiesWidget
from views.NewPropertyFormView.NewPropertyFormView import NewPropertyFormView


class NewPropertyController(QObject):
    property_added = pyqtSignal(str, str, object, PropertiesWidget,int)

    def __init__(self, widget: PropertiesWidget, index: int):
        super().__init__()
        self.model = ItemModel()
        self.view = NewPropertyFormView()
        self.widget = widget
        self.index = index

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.view.item_type_ComboBox.addItems(self.model.get_item_types())

    def setup_connections(self):
        self.view.buttonBox.accepted.connect(self.handle_ok)
        self.view.buttonBox.rejected.connect(self.view.close)

    def handle_ok(self):
        item_name = self.view.item_name_LineEdit.text().strip()
        label_text = self.view.label_text_LineEdit.text().strip()
        item_type = self.view.item_type_ComboBox.currentText()

        if item_name and label_text:
            item_class = self.model.get_item_class(item_type)
            if item_class:
                self.property_added.emit(label_text, item_name, item_class, self.widget, self.index)
                self.view.close()

    def close_window(self):
        self._view.close()
