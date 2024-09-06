from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox

from model.Model import Model
from resources.TabWidget import TabWidget
from resources.ValidatedLineEdit import ValidatedLineEdit


class NewTabDialog(QDialog):
    tab_added = pyqtSignal(str, TabWidget)

    def __init__(self, widget: TabWidget):
        super().__init__()
        self.widget = widget

        self._setup_ui()
        self._setup_connections()
        self.show()

    def _setup_ui(self):
        self.setWindowTitle("Nowa Karta")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.tab_name_field = ValidatedLineEdit("Nazwa Karty")
        form_layout.addRow(self.tab_name_field.label, self.tab_name_field.line_edit)
        form_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.tab_name_field.error_label)

        layout.addLayout(form_layout)

        # Dialog buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def _setup_connections(self):
        self.buttonBox.accepted.connect(self.handle_ok)
        self.buttonBox.rejected.connect(self.close_window)
        self.tab_name_field.line_edit.textChanged.connect(self.clear_error)

    def handle_ok(self):
        tab_name = self.tab_name_field.text()

        if not tab_name:
            self.tab_name_field.set_error("Nazwa elementu nie może być pusta.")
            return

        if Model.find_tab(tab_name) is not None:
            self.tab_name_field.set_error("Ta nazwa elementu już istnieje.")
            return

        self.tab_added.emit(tab_name, self.widget)
        self.close_window()

    def clear_error(self):
        self.tab_name_field.clear_error()

    def close_window(self):
        self.close()
