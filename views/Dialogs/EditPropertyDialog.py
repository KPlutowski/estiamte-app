from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QFormLayout
from PyQt6.QtCore import pyqtSignal

from model.Model import Model
from resources.TabWidget import GroupBox
from resources.ValidatedLineEdit import ValidatedLineEdit


class EditPropertyDialog(QDialog):
    property_edited = pyqtSignal(str, str, int)

    def __init__(self, index: int, widget: GroupBox):
        super().__init__()
        self.widget = widget
        self.index = index
        self._setup_ui()
        self._setup_connections()
        self.show()

    def _setup_ui(self):
        self.setWindowTitle("Edytuj Właściwość")
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

        layout.addLayout(form_layout)

        # Dialog buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

        self.item_name_field.set_text(self.widget.item.name)
        self.label_text_LineEdit.set_text(self.widget.label.text())

    def _setup_connections(self):
        self.buttonBox.accepted.connect(self.handle_ok)
        self.buttonBox.rejected.connect(self.close_window)
        self.item_name_field.line_edit.textChanged.connect(self.clear_error)

    def handle_ok(self):
        item_name = self.item_name_field.text()
        label_text = self.label_text_LineEdit.text().strip()

        if not item_name:
            self.item_name_field.set_error("Nazwa elementu nie może być pusta.")
            return

        if item_name == self.widget.item.name:
            self.close_window()
            return

        if Model.find_item(item_name) is not None:
            self.item_name_field.set_error("Ta nazwa elementu już istnieje.")
            return

        self.property_edited.emit(label_text, item_name, self.index)
        self.close_window()

    def clear_error(self):
        self.item_name_field.clear_error()

    def close_window(self):
        self.close()
