from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDialogButtonBox, QComboBox, QLabel, QFormLayout, QLineEdit

from model.ItemModel import ItemModel
from resources.ValidatedLineEdit import ValidatedLineEdit


class NewPropertyFormView(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
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

        self.item_type_ComboBox = self._create_combo_box()
        form_layout.addRow(QLabel("Typ", self), self.item_type_ComboBox)

        layout.addLayout(form_layout)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self.buttonBox)

    def _create_line_edit(self) -> QLineEdit:
        line_edit = QLineEdit(self)
        line_edit.setClearButtonEnabled(True)
        return line_edit

    def _create_combo_box(self) -> QComboBox:
        combo_box = QComboBox(self)
        combo_box.addItems(ItemModel.get_item_types())
        return combo_box