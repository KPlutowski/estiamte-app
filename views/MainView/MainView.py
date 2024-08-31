from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QEvent, Qt, QMimeData
from PyQt6.QtGui import QMouseEvent, QDrag, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QGridLayout, QWidget, QMenu, QVBoxLayout

from model.CheckBoxItem import CheckBoxItem
from model.DoubleSpinnBoxItem import DoubleSpinnBoxItem
from model.GroupBox import MovableWidget
from model.LineEditItem import LineEditItem
from model.Model import Model, db
from model.Spreadsheet import Spreadsheet
from views.MainView.main_window_ui import Ui_MainWindow
import resources.constants as constants


class MainView(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.line_edits = [
            self.perimeter,
            self.foundationArea,
            self.rafterCount,
            self.rafterLength,
            self.groundWallArea,
            self.kneeWallArea,
            self.gableArea,
            self.externalWallArea,
            self.eavesLenght,
            self.spoutLength
        ]
        self.checkboxes = [
            self.attic,
            self.largeHouse,
            self.chimney
        ]
        self.spin_boxes = [
            self.gridArea,
            self.buildingLength,
            self.buildingWidth,
            self.glassQuantity,
            self.groundFloorWalls,
            self.roofLength,
            self.firstFloorWalls,
            self.kneeWallHeight,
            self.groundFloorHeight
        ]
        self.spreadsheets = []

        self.eventTrap = None
        self.target = None
        self.dragged_widget = None

        self.scrollArea.customContextMenuRequested.connect(self.properties_context_menu)

        self.initUI()
        self.show()

    def make_spreadsheet(self, name: str, tab_widget: QTabWidget):
        def create_table_widget(parent_: QtWidgets.QWidget) -> QtWidgets.QTableWidget:
            table_widget = Spreadsheet(parent=parent_)
            table_widget.setObjectName(name)
            table_widget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            table_widget.setAlternatingRowColors(True)
            table_widget.setColumnCount(len(constants.COLUMNS))
            table_widget.horizontalHeader().setStretchLastSection(True)
            table_widget.setRowCount(0)
            return table_widget

        def set_column_headers(table_widget: QtWidgets.QTableWidget):
            for index, (header_name, _) in enumerate(constants.COLUMNS):
                item = QtWidgets.QTableWidgetItem()
                item.setText(header_name)
                table_widget.setHorizontalHeaderItem(index, item)

        if name in db:
            raise KeyError(f"Spreadsheet found with name '{name}'.")

        new_tab = QtWidgets.QWidget()
        new_tab.setObjectName(name)
        new_table_widget = create_table_widget(new_tab)

        vertical_layout = QtWidgets.QVBoxLayout(new_tab)
        vertical_layout.addWidget(new_table_widget)

        set_column_headers(new_table_widget)

        tab_widget.addTab(new_tab, name)
        self.spreadsheets.append(new_table_widget)

    def initUI(self):
        self.make_spreadsheet(constants.POSITION_SPREADSHEET_NAME, self.tabWidget)
        self.make_spreadsheet(constants.ROOF_SPREADSHEET_NAME, self.tabWidget)
        self.make_spreadsheet(constants.FOUNDATION_SPREADSHEET_NAME, self.tabWidget)
        self.make_spreadsheet(constants.INSULATION_SPREADSHEET_NAME, self.tabWidget)

        self.add_to_model()

    def add_to_model(self):
        for spreadsheet in self.spreadsheets:
            Model.add_item(spreadsheet)

        for spin_box in self.spin_boxes:
            Model.add_item(spin_box)

        for checkbox in self.checkboxes:
            Model.add_item(checkbox)

        for line_edit in self.line_edits:
            Model.add_item(line_edit)

    def update_formula_bar(self, value):
        self.Formula_bar.setText(f'{value}')

    def update_name_box(self, value):
        self.Name_box.setText(f'{value}')

    def properties_context_menu(self, pos: QtCore.QPoint):
        menu = QMenu()
        add_double_spinn_box_action = menu.addAction('Add DoubleSpinnBox')
        add_check_box_action = menu.addAction('Add CheckBox')
        add_line_edit_action = menu.addAction('Add LineEdit')

        action = menu.exec(self.scrollArea.mapToGlobal(pos))
        if not action:
            return

        position = 2

        if action == add_double_spinn_box_action:
            myobj = MovableWidget(0, "newLabel", "newItemName", DoubleSpinnBoxItem)
            # myobj.item.activeItemChangedSignal.connect(self.activeItemChanged)
        elif action == add_check_box_action:
            myobj = MovableWidget(0, "newLabel", "newItemName", CheckBoxItem)
            # myobj.item.activeItemChangedSignal.connect(self.activeItemChanged)

        elif action == add_line_edit_action:
            myobj = MovableWidget(0, "newLabel", "newItemName", LineEditItem)
            # myobj.item.textEditedSignal.connect(self.itemWithFormulaTextEdited)
            # myobj.item.textEditingFinishedSignal.connect(self.itemWithFormulaTextEditedFinished)
            # myobj.item.doubleClickedSignal.connect(self.itemWithFormulaDoubleClicked)
            # myobj.item.activeItemChangedSignal.connect(self.activeItemWithFormulaChanged)
        else:
            return
        Model.add_item(myobj.item)

        self.scrollVerticalLayout.insertWidget(position, myobj)

    def eventFilter(self, watched, event: QEvent):
        if event.type() == QEvent.Type.MouseButtonPress:
            self.mousePressEvent(event)
        elif event.type() == QEvent.Type.MouseMove:
            self.mouseMoveEvent(event)
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self.mouseReleaseEvent(event)
        return super().eventFilter(watched, event)

    def get_index(self, global_pos):
        """Return the index of the widget under the given global position."""
        # print(f"global_pos = {global_pos}")
        for i in range(self.scrollVerticalLayout.count()):
            widget = self.scrollVerticalLayout.itemAt(i).widget()

            top_left = widget.mapTo(self, widget.rect().topLeft())
            bottom_right = widget.mapTo(self, widget.rect().bottomRight())

            # Create a QRect using these points
            widget_rect = QtCore.QRect(top_left, bottom_right)
            # print(f"Widget {i}: Top Left {widget_rect.topLeft()}, Bottom Right {widget_rect.bottomRight()}, global_pos {global_pos}")

            if widget_rect.contains(global_pos):
                print(f"Selected target index: {i}")
                return i

        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.eventTrap is None:
                self.eventTrap = event
                self.target = self.get_index(event.pos())
            elif self.eventTrap == event:
                pass
            else:
                print("Something broke")
        else:
            self.target = None

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.target is not None:
            # Get the widget being dragged
            self.dragged_widget = self.scrollVerticalLayout.itemAt(self.target).widget()

            # Create a QDrag object and set up the drag
            drag = QDrag(self.dragged_widget)
            pix = self.dragged_widget.grab()

            # Set up the mime data for the drag operation
            mimedata = QMimeData()
            mimedata.setImageData(pix)
            drag.setMimeData(mimedata)

            # Set the pixmap and calculate the hotspot relative to the widget
            drag.setPixmap(pix)
            local_pos = event.pos() - self.dragged_widget.mapTo(self, self.dragged_widget.rect().topLeft())
            drag.setHotSpot(local_pos)

            # Temporarily hide the widget to prevent the afterimage effect
            self.dragged_widget.setVisible(False)
            drag.exec()
            self.dragged_widget.setVisible(True)

            # Reset the drag state
            self.target = None
            self.dragged_widget = None

    def mouseReleaseEvent(self, event):
        self.eventTrap = None
        self.target = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasImage():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        drop_position = event.position().toPoint()

        # Calculate the insertion index
        widget_count = self.scrollVerticalLayout.count()
        if widget_count == 0:
            # If there are no widgets, insert at index 0
            target_index = 0
        else:
            # Initialize to the last index by default
            target_index = widget_count - 1

            for i in range(widget_count):
                widget = self.scrollVerticalLayout.itemAt(i).widget()

                # Calculate the rectangle of the current widget
                top_left = widget.mapTo(self, widget.rect().topLeft())
                bottom_right = widget.mapTo(self, widget.rect().bottomRight())

                # Check if the drop position is above the first widget
                if drop_position.y() <= top_left.y() and i == 0:
                    target_index = 0
                    break
                # Check if the drop position is between the current widget and the next one
                elif drop_position.y() <= bottom_right.y():
                    target_index = i
                    break

        self.scrollVerticalLayout.insertWidget(target_index, self.dragged_widget)

        # Reset the drag state
        self.target = None
        self.eventTrap = None
