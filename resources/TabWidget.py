from typing import Dict

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint, QEvent
from PyQt6.QtGui import QMouseEvent, QDrag, QDropEvent, QDragEnterEvent
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QLabel, QInputDialog, QLineEdit, \
    QSplitter

from model.ItemModel import ItemModel


class GroupBox(QWidget):
    context_menu_request = pyqtSignal(QtCore.QPoint, object)

    def __init__(self, label_text="", item_name="", item_type=None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.drag_start_position: QPoint
        self.label = QLabel(parent=self)
        self.label.setText(label_text)

        self.item = item_type(parent=self)
        self.setObjectName(f"GroupBox_{item_name}")
        self.item.setObjectName(item_name)

        if item_type == ItemModel.get_item_class("Spreadsheet"):
            self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.addWidget(self.label)
            self.layout.addWidget(self.item)

            sizePolicy = QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.item.sizePolicy().hasHeightForWidth())
        else:
            self.layout = QtWidgets.QHBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.addWidget(self.label)
            self.layout.addWidget(self.item)

            sizePolicy = QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.item.sizePolicy().hasHeightForWidth())

    @property
    def name(self):
        return self.objectName()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            distance = (event.globalPosition().toPoint() - self.drag_start_position).manhattanLength()
            if distance >= QtWidgets.QApplication.startDragDistance():
                self.start_drag()

    def start_drag(self):
        from model.Model import Model
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setData('application/x-estimatex-dragged-widget', self.objectName().encode())
        drag.setMimeData(mime_data)

        pixmap = self.grab()
        drag.setPixmap(pixmap)

        local_pos = self.drag_start_position - self.mapToGlobal(self.rect().topLeft())
        drag.setHotSpot(local_pos)

        self.setVisible(False)
        Model.remove_item(self.name)

        drag.exec(Qt.DropAction.MoveAction)
        self.setVisible(True)


class MyTab(QWidget):
    context_menu_request = pyqtSignal(QtCore.QPoint, object)

    def __init__(self, parent, name: str):
        super().__init__(parent)
        self.group_boxes: Dict[str, GroupBox] = {}

        # Main layout for MyTab
        self.main_layout = QVBoxLayout(self)

        # Create and set up the vertical splitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(5)
        self.splitter.setChildrenCollapsible(False)

        # Scroll area and its content
        self.scroll_area = QScrollArea(self)
        self.scroll_area_content = QWidget()

        # Set the layout for the scroll area content
        self.scroll_area_content.setLayout(QVBoxLayout(self.scroll_area_content))
        self.scroll_area_content.layout().addWidget(self.splitter)

        # Add the scroll area to the main layout
        self.main_layout.addWidget(self.scroll_area)

        # Configure the scroll area
        self.scroll_area.setWidget(self.scroll_area_content)
        self.scroll_area.setWidgetResizable(True)

        # Enable context menu and drag-and-drop
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)
        self.setAcceptDrops(True)
        self.scroll_area.setAcceptDrops(True)
        self.scroll_area_content.setAcceptDrops(True)

        self.setObjectName(name)

    def context_menu(self, pos):
        self.context_menu_request.emit(pos, self)

    @property
    def name(self):
        return self.objectName()

    def add_group_box(self, group_box: GroupBox, index: int = -1):
        if group_box.name in self.group_boxes:
            raise KeyError(f"group_box found with name '{group_box.name}'.")

        if self.splitter is None:
            raise RuntimeError("Splitter is not initialized.")

        if index == -1 or index >= self.splitter.count():
            self.splitter.addWidget(group_box)
        else:
            self.splitter.insertWidget(index, group_box)

        self.group_boxes[group_box.name] = group_box

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        drop_position = event.position().toPoint()
        mime_data = event.mimeData()
        dragged_widget = None

        if mime_data.data('application/x-estimatex-dragged-widget'):
            widget_name = mime_data.data('application/x-estimatex-dragged-widget').data().decode()

            dragged_widget = self.findChild(GroupBox, widget_name)

            if not dragged_widget:
                # If not found, search in other tabs
                for i in range(self.parent().parent().count()):
                    tab = self.parent().parent().widget(i)
                    dragged_widget = tab.findChild(GroupBox, widget_name)
                    if dragged_widget:
                        break

        if not dragged_widget:
            print("Dragged widget not found.")
            return

        map_pos = self.splitter.mapFromGlobal(self.mapToGlobal(drop_position))
        widget_under_cursor = self.splitter.childAt(map_pos)

        if widget_under_cursor:
            index = self.splitter.indexOf(widget_under_cursor.parent())
        else:
            index = self.splitter.count() - 1  # Default to last position if no widget found

        self.group_boxes[dragged_widget.name] = dragged_widget

        if 0 <= index < self.splitter.count():
            self.splitter.insertWidget(index, dragged_widget)
        else:
            self.splitter.addWidget(dragged_widget)

        event.acceptProposedAction()

    def reset_spliter(self):
        widget_count = self.splitter.count()
        if widget_count == 0:
            return

        available_height = self.splitter.height()
        equal_size = available_height // widget_count
        sizes = [equal_size] * widget_count
        self.splitter.setSizes(sizes)

    def delete_property(self, index: int):
        if index is None:
            return
        widget_to_delete = self.splitter.widget(index)

        # Ensure the widget exists
        if widget_to_delete is None:
            print(f"No widget found at index {index}")
            return

        # Remove the widget from the splitter
        self.splitter.widget(index).setParent(None)

        # Remove the widget from the group_boxes dictionary
        if widget_to_delete.name in self.group_boxes:
            widget_to_delete.item.clean_up()
            del self.group_boxes[widget_to_delete.name]
        else:
            print(f"GroupBox '{widget_to_delete.name}' not found in group_boxes")


class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

        self.setAcceptDrops(True)
        self.tabBar().setChangeCurrentOnDrag(True)
        self.tabBar().setAcceptDrops(True)
        self.tabBar().installEventFilter(self)

    def initUI(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        self.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabBarAutoHide(True)
        self.setObjectName("tabWidget")

    def add_tab(self, name) -> MyTab:
        my_tab = MyTab(self, name)
        self.addTab(my_tab, name)
        return my_tab

    def get_tab_by_name(self, name: str):
        for i in range(self.count()):
            widget = self.widget(i)
            if widget.objectName() == name:
                return widget.children()[0]
        return None

    def mouseDoubleClick(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.rename_tab(event)
        else:
            super().mouseDoubleClickEvent(event)

    def eventFilter(self, watched, event: QEvent):
        if watched == self.tabBar():
            if event.type() == QEvent.Type.MouseButtonDblClick:
                self.mouseDoubleClick(event)
        return super().eventFilter(watched, event)

    def rename_tab(self, event):
        from model.Model import Model
        tab_bar = self.tabBar()
        index = tab_bar.tabAt(event.position().toPoint())
        if index != -1:  # Ensure the click was on a tab
            current_name = tab_bar.tabText(index)
            new_name, ok = QInputDialog.getText(
                self, "Change Name",
                "Insert New Tab Name:",
                QLineEdit.EchoMode.Normal,
                current_name
            )
            if ok and new_name:
                Model.rename_tab(current_name, new_name)
                tab_bar.setTabText(index, new_name)
                self.setTabText(index, new_name)
