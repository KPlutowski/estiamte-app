from PyQt6.QtWidgets import QMainWindow

from views.MainView.main_window_ui import Ui_MainWindow
import resources.constants as constants

class MainView(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.initUI()
        self.show()

    def initUI(self):
        self.PositionsTableWidget.setRowCount(0)
        self.PropertiesTableWidget.setRowCount(0)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.properties_tab), constants.SPREADSHEET_PROPERTY_TABLE_NAME)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.position_tab), constants.SPREADSHEET_POSITION_TABLE_NAME)

    def update_formula_bar(self, value):
        self.Formula_bar.setText(f'{value}')

    def update_name_box(self, value):
        self.Name_box.setText(f'{value}')
