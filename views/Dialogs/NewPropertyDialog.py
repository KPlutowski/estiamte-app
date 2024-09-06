from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QComboBox, QLabel, QFormLayout, QLineEdit
from PyQt6.QtCore import pyqtSignal

from model.ItemModel import ItemModel
from model.Model import Model
from resources.TabWidget import MyTab
from resources.ValidatedLineEdit import ValidatedLineEdit


class NewPropertyDialog(QDialog):
    property_added = pyqtSignal(str, str, object, MyTab, int)

    def __init__(self, widget: MyTab, index: int = 0):
        super().__init__()
        self.widget = widget
        self.index = index

        self._setup_ui()
        self._setup_connections()
        self.show()

    def _setup_ui(self):
        self.setWindowTitle("Nowa Właściwość")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Initialize fields
        self.item_name_field = ValidatedLineEdit("Nazwa pola")
        form_layout.addRow(self.item_name_field.label, self.item_name_field.line_edit)
        form_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.item_name_field.error_label)

        self.label_text_LineEdit = ValidatedLineEdit("Opis")
        form_layout.addRow(self.label_text_LineEdit.label, self.label_text_LineEdit.line_edit)
        form_layout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label_text_LineEdit.error_label)

        # Combo box for item type
        self.item_type_ComboBox = QComboBox(self)
        self.item_type_ComboBox.addItems(ItemModel.get_item_types())
        form_layout.addRow(QLabel("Typ", self), self.item_type_ComboBox)

        layout.addLayout(form_layout)

        # Dialog buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def _setup_connections(self):
        self.buttonBox.accepted.connect(self.handle_ok)
        self.buttonBox.rejected.connect(self.close_window)
        self.item_name_field.line_edit.textChanged.connect(self.clear_error)

    def handle_ok(self):
        item_name = self.item_name_field.text()
        label_text = self.label_text_LineEdit.text().strip()
        item_type = self.item_type_ComboBox.currentText()

        if not item_name:
            self.item_name_field.set_error("Nazwa elementu nie może być pusta.")
            return

        if Model.find_item(item_name) is not None:
            self.item_name_field.set_error("Ta nazwa elementu już istnieje.")
            return

        item_class = ItemModel.get_item_class(item_type)
        if item_class:
            self.property_added.emit(label_text, item_name, item_class, self.widget, self.index)
            self.close_window()

    def clear_error(self):
        self.item_name_field.clear_error()

    def close_window(self):
        self.close()
