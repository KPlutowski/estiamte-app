from typing import Dict

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint, QEvent
from PyQt6.QtGui import QMouseEvent, QDrag, QDropEvent, QDragEnterEvent
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QLabel, QSplitter, QMenu

from model.ItemModel import ItemModel

from views.Dialogs.RenameTabDialog import RenameTabDialog


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
        else:
            self.layout = QtWidgets.QHBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.item)

        sizePolicy = QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item.sizePolicy().hasHeightForWidth())
        self.item.setSizePolicy(sizePolicy)

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

    def delete(self):
        self.setParent(None)
        self.item.clean_up()


class MyTab(QWidget):
    propertyAdded = pyqtSignal(object)

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
        self.scroll_area_content.setLayout(QVBoxLayout(self.scroll_area_content))
        self.scroll_area_content.layout().addWidget(self.splitter)

        # Add the scroll area to the main layout
        self.main_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_area_content)
        self.scroll_area.setWidgetResizable(True)

        # Enable context menu and drag-and-drop
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)
        self.setAcceptDrops(True)
        self.scroll_area.setAcceptDrops(True)
        self.scroll_area_content.setAcceptDrops(True)

        self.setObjectName(name)

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

        if widget_to_delete is None:
            return
        widget_to_delete.delete()

        del self.group_boxes[widget_to_delete.name]

    def delete_tab(self):
        from model.Model import Model
        for i in range(len(self.group_boxes)):
            self.delete_property(0)
        Model.remove_tab(self.name)

    def context_menu(self, pos):
        menu = QMenu()
        add_new_property_action = menu.addAction('Dodaj właściwość')
        delete_property_action = menu.addAction('Usuń właściwość')
        reset_spliter_action = menu.addAction('Przywróć domyślny układ')

        index = self.get_index(self.mapToGlobal(pos))

        action = menu.exec(self.mapToGlobal(pos))
        if action == add_new_property_action:
            from views.Dialogs.NewPropertyDialog import NewPropertyDialog
            self.property_dialog = NewPropertyDialog(index)
            self.property_dialog.property_added.connect(self.add_property)
        elif action == reset_spliter_action:
            self.reset_spliter()
        elif action == delete_property_action:
            self.delete_property(index)

    def add_property(self, label_text: str, item_name: str, item_type, index: int = 0):
        if item_type is None:
            raise KeyError(f"Missing item_type.")
        tmp = GroupBox(label_text, item_name, item_type, self)

        self.propertyAdded.emit(tmp)
        self.add_group_box(tmp, index)

    def eventFilter(self, a0, a1):
        pass

    def get_index(self, pos):
        if not isinstance(self, MyTab):
            return None

        closest_index = None
        min_distance = float('inf')

        # Iterate through the widgets in the layout
        for i in range(self.splitter.count()):
            widget = self.splitter.widget(i)

            # Get the global coordinates of the widget's top-left and bottom-right corners
            top_left = widget.mapToGlobal(widget.rect().topLeft())
            bottom_right = widget.mapToGlobal(widget.rect().bottomRight())

            # Create a QRect representing the widget's global geometry
            widget_rect = QtCore.QRect(top_left, bottom_right)

            if widget_rect.contains(pos):
                # If the position is inside the widget, return its index immediately
                return i

            # Otherwise, calculate the distance from the click position to the widget's rect
            # Use the center of the widget for a more accurate "closeness" measure
            widget_center = widget_rect.center()
            distance = (pos - widget_center).manhattanLength()

            # Keep track of the widget with the minimum distance
            if distance < min_distance:
                min_distance = distance
                closest_index = i

        return closest_index


class TabWidget(QTabWidget):
    propertyAdded = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

        self.setAcceptDrops(True)
        self.tabBar().setChangeCurrentOnDrag(True)
        self.tabBar().setAcceptDrops(True)
        self.tabBar().installEventFilter(self)
        self.tabBar().customContextMenuRequested.connect(self.tabBar_context_menu)

    def initUI(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        self.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabBarAutoHide(True)
        self.setObjectName("tabWidget")

    def get_tab_by_name(self, name: str) -> MyTab:
        for i in range(self.count()):
            tab = self.widget(i)
            if tab.objectName() == name:
                return tab
        return None

    def eventFilter(self, watched, event: QEvent):
        if watched == self.tabBar():
            if event.type() == QEvent.Type.MouseButtonDblClick:
                index = self.tabBar().tabAt(event.position().toPoint())
                if index != -1:  # Ensure the click was on a tab
                    self.rename_tab_dialog = RenameTabDialog(index)
                    self.rename_tab_dialog.tab_renamed.connect(self.rename_tab)
        return super().eventFilter(watched, event)

    def rename_tab(self, new_name, index):
        from model.Model import Model
        current_name = self.tabBar().tabText(index)
        Model.rename_tab(current_name, new_name)
        self.tabBar().setTabText(index, new_name)
        self.setTabText(index, new_name)

    def tabBar_context_menu(self, pos: QtCore.QPoint):
        global_pos = self.tabBar().mapToGlobal(pos)

        index_of_clicked_tab = self.tabBar().tabAt(pos)

        if index_of_clicked_tab != -1:
            # Get the name of the clicked tab
            name_of_clicked_tab = self.tabText(index_of_clicked_tab)

            # Create the context menu
            menu = QMenu()
            add_tab_action = menu.addAction('Dodaj nową karte')
            delete_tab_action = menu.addAction(f'Usuń karte "{name_of_clicked_tab}"')

            # Execute the menu
            action = menu.exec(global_pos)

            if action == add_tab_action:
                from views.Dialogs.NewTabDialog import NewTabDialog
                self.tab_dialog = NewTabDialog()
                self.tab_dialog.tab_added.connect(self.add_new_tab)
            elif action == delete_tab_action:
                tab_name = self.tabText(index_of_clicked_tab)
                reply = QtWidgets.QMessageBox.question(
                    self,
                    "Potwierdzenie usunięcia karty",
                    f"Czy na pewno chcesz usunąć kartę '{tab_name}'?",
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                )

                if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                    self.delete_tab(index_of_clicked_tab)
        else:
            print("No tab was clicked.")

    def add_new_tab(self, name: str):
        from model.Model import Model
        my_tab = MyTab(self, name)
        my_tab.propertyAdded.connect(self.propertyAdded.emit)
        self.addTab(my_tab, name)
        Model.add_tab_to_db(my_tab)

    def delete_tab(self, index: int):
        if 0 <= index < self.count():
            tab_name = self.tabText(index)
            self.get_tab_by_name(tab_name).delete_tab()
            self.removeTab(index)
