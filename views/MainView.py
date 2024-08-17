from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import pyqtSlot

from controlers.MainController import MainController
from model.Model import Model
from views.ui.main_window_ui import Ui_MainWindow


class MainView(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._model = Model()
        self._main_controller = MainController(self._model, self)

        self.initUI()

        # set a default value
        self.load_test_data()

    def initUI(self):
        self.ui.PositonsTableWidget.setRowCount(0)
        self.ui.PropertiesTableWidget.setRowCount(0)

    def load_test_data(self):
        self._model.add_spreadsheet(self.ui.tabWidget.tabText(0), self.ui.PositonsTableWidget)
        self._model.add_spreadsheet(self.ui.tabWidget.tabText(1), self.ui.PropertiesTableWidget)
        for name, spreadsheet in self._model.spreadsheets.items():
            for i in range(20):
                spreadsheet.add_row(i)
        self._main_controller.on_tab_changed(self.ui.tabWidget.currentIndex())

    @pyqtSlot(int)
    def on_tab_changed(self, index: int):
        tab_name = self.ui.tabWidget.tabText(index)
        self._main_controller.handle_tab_change(tab_name)

    def update_formula_bar(self, value):
        self.ui.Formula_bar.setText(f'{value}')

    def update_name_box(self, value):
        self.ui.Name_box.setText(f'{value}')
