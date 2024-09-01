from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDialogButtonBox, QComboBox, QLineEdit, QLabel, QFormLayout


class NewPropertyFormView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.show()

    def setup_ui(self):
        self.setWindowTitle("Nowa Właściwość")
        self.setGeometry(100, 100, 400, 300)

        self.vertical_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.label_name = QLabel("Nazwa pola", self)
        self.item_name_LineEdit = QLineEdit(self)
        self.item_name_LineEdit.setClearButtonEnabled(True)
        self.form_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_name)
        self.form_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.item_name_LineEdit)

        self.label_text = QLabel("Opis", self)
        self.label_text_LineEdit = QLineEdit(self)
        self.label_text_LineEdit.setClearButtonEnabled(True)
        self.form_layout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_text)
        self.form_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label_text_LineEdit)

        self.label_type = QLabel("Typ", self)
        self.item_type_ComboBox = QComboBox(self)
        self.form_layout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_type)
        self.form_layout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.item_type_ComboBox)

        self.vertical_layout.addLayout(self.form_layout)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.vertical_layout.addWidget(self.buttonBox)
