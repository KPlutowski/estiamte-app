from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout


class ValidatedLineEdit(QWidget):
    def __init__(self, label_text: str, parent: QWidget = None):
        super().__init__(parent)
        self.label = QLabel(label_text, self)
        self.line_edit = QLineEdit(self)
        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setVisible(False)  # Initially hidden
        self._setup_layout()

    def _setup_layout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.error_label)
        self.setLayout(layout)
        self.line_edit.setClearButtonEnabled(True)

    def set_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        self.line_edit.setStyleSheet("border: 2px solid red;")

    def clear_error(self):
        self.error_label.setVisible(False)
        self.line_edit.setStyleSheet("")

    def text(self) -> str:
        return self.line_edit.text().strip()

    def set_text(self, text: str):
        self.line_edit.setText(text)
