from PyQt6 import QtWidgets

from views.ui.new_estimate_ui import Ui_new_cost_estimate_window


class NewEstimateView(QtWidgets.QWidget, Ui_new_cost_estimate_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    # TODO
    def accept(self):
        print("accept")

    # TODO
    def reject(self):
        print("reject")

