from PyQt6 import QtWidgets
from views.NewEstiamteView.new_estimate_ui import Ui_new_cost_estimate_window


class NewEstimateView(QtWidgets.QWidget, Ui_new_cost_estimate_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
