from typing import Dict, Optional

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint, QEvent
from PyQt6.QtGui import QMouseEvent, QDrag, QDropEvent, QDragEnterEvent
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QLabel, QInputDialog, QLineEdit

from model.ItemModel import ItemModel


class GroupBox(QWidget):
    context_menu_request = pyqtSignal(QtCore.QPoint, object)
    drag_started = pyqtSignal(QWidget)

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
        drag = QDrag(self)
        mime_data = QMimeData()
        drag.setMimeData(mime_data)

        pixmap = self.grab()
        drag.setPixmap(pixmap)

        local_pos = self.drag_start_position - self.mapToGlobal(self.rect().topLeft())

        drag.setHotSpot(local_pos)

        self.drag_started.emit(self)
        self.setVisible(False)
        drag.exec(Qt.DropAction.MoveAction)
        self.setVisible(True)


class MyTab(QWidget):
    context_menu_request = pyqtSignal(QtCore.QPoint, object)

    def __init__(self, parent):
        super().__init__(parent)
        self.group_boxes: Dict[str, GroupBox] = {}

        # Main layout for MyTab
        self.main_layout = QVBoxLayout(self)

        # Layout for the content within the scroll area
        self.scroll_area_content_layout = QVBoxLayout()

        # Scroll area and its content
        self.scroll_area = QScrollArea(self)
        self.scroll_area_content = QWidget()

        # Set the layout for the scroll area content
        self.scroll_area_content.setLayout(self.scroll_area_content_layout)

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

    def context_menu(self, pos):
        self.context_menu_request.emit(pos, self)

    @property
    def name(self):
        return self.objectName()

    def add_group_box(self, group_box: GroupBox, index: int):
        if group_box.name in self.group_boxes:
            raise KeyError(f"group_box found with name '{group_box.name}'.")

        layout = self.scroll_area_content_layout
        if layout is None:
            raise RuntimeError("Layout is not initialized.")

        if index < 0 or index > layout.count():
            raise IndexError("Index out of bounds.")

        layout.insertWidget(index, group_box)
        self.group_boxes[group_box.name] = group_box

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        from model.Model import Model
        drop_position = self.mapToGlobal(event.position().toPoint())
        layout = self.scroll_area_content_layout

        target_index = layout.count()-1
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()

            top_left = widget.mapToGlobal(widget.rect().topLeft())

            if drop_position.y() < top_left.y():
                target_index = i
                break

        # Add the dragged widget to the new position
        dragged_widget = self.parent().parent().dragged_widget

        Model.remove_item(dragged_widget.name)
        self.group_boxes[dragged_widget.name] = dragged_widget

        layout.insertWidget(target_index, dragged_widget)
        event.acceptProposedAction()


class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.dragged_widget: Optional[GroupBox] = None

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
        my_tab = MyTab(self)
        my_tab.setObjectName(name)
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
        if watched==self.tabBar():
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
                Model.rename_tab(current_name,new_name)
                tab_bar.setTabText(index, new_name)
                self.setTabText(index, new_name)
