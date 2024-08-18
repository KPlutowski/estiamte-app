from PyQt6.QtCore import QObject
from model import Model
from views.NewEstiamteView.NewEstimateView import NewEstimateView

class NewEstimateController(QObject):
    def __init__(self, model: Model):
        super().__init__()
        self._model = model
        self._view = NewEstimateView()

    def setup_connections(self):
        pass
