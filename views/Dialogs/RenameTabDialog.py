from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox


from resources.ValidatedLineEdit import ValidatedLineEdit


class RenameTabDialog(QDialog):
    tab_renamed = pyqtSignal(str, int)

    def __init__(self, index):
        super().__init__()
        self.index = index
        self._setup_ui()
        self._setup_connections()
        self.show()

    def _setup_ui(self):
        self.setWindowTitle("Zmień nazwe")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.new_tab_name_field = ValidatedLineEdit("Nowa Nazwa")
        form_layout.addRow(self.new_tab_name_field.label, self.new_tab_name_field.line_edit)
        form_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.new_tab_name_field.error_label)

        layout.addLayout(form_layout)

        # Dialog buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def _setup_connections(self):
        self.buttonBox.accepted.connect(self.handle_ok)
        self.buttonBox.rejected.connect(self.close_window)
        self.new_tab_name_field.line_edit.textChanged.connect(self.clear_error)

    def handle_ok(self):
        from model.Model import Model

        new_tab_name = self.new_tab_name_field.text()

        if not new_tab_name:
            self.new_tab_name_field.set_error("Nazwa elementu nie może być pusta.")
            return

        if Model.find_tab(new_tab_name) is not None:
            self.new_tab_name_field.set_error("Ta nazwa elementu już istnieje.")
            return

        self.tab_renamed.emit(new_tab_name, self.index)
        self.close_window()

    def clear_error(self):
        self.new_tab_name_field.clear_error()

    def close_window(self):
        self.close()
