from PyQt6 import QtWidgets
from views.NewEstiamteView.new_estimate_ui import Ui_new_cost_estimate_window

class NewEstimateView(QtWidgets.QWidget, Ui_new_cost_estimate_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_connections()
        self.show()

    def setup_connections(self):
        # Connect buttons to their respective slots
        self.buttonBox.accepted.connect(self.handle_ok)
        self.buttonBox.rejected.connect(self.close_window)

    def handle_ok(self):
        # Process data from the form when OK is pressed
        building_length = self.SpinBox_building_length.value()
        building_width = self.SpinBox_building_width.value()
        number_of_footings = self.spinBox_number_of_footings.value()
        first_floor_partitions = self.SpinBox_first_floor_partitions.value()
        length_of_roof_slope = self.SpinBox_length_of_roof_slope.value()
        knee_wall_height = self.SpinBox_knee_wall_height.value()
        first_floor_wall_height = self.SpinBox_first_floor_wall_height.value()

        is_over_70m2 = self.checkBox_is_the_house_over_70m2.isChecked()
        is_attic_usable = self.checkBox_is_the_attic_usable.isChecked()
        has_chimney = self.checkBox_has_chimney.isChecked()

        # TODO: Implement logic to process or save the collected data
        print(f"Building Length: {building_length}")
        print(f"Building Width: {building_width}")
        print(f"Number of Footings: {number_of_footings}")
        print(f"First Floor Partitions: {first_floor_partitions}")
        print(f"Length of Roof Slope: {length_of_roof_slope}")
        print(f"Knee Wall Height: {knee_wall_height}")
        print(f"First Floor Wall Height: {first_floor_wall_height}")
        print(f"House Over 70m²: {is_over_70m2}")
        print(f"Attic Usable: {is_attic_usable}")
        print(f"Has Chimney: {has_chimney}")

        self.close_window()

    def close_window(self):
        self.close()
