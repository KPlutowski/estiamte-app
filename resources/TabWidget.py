from typing import Set, Optional, Dict, Any, List

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
        self.drag_start_position: Optional[QPoint] = None

        self.label = QLabel(parent=self)
        self.label.setText(label_text)

        self.item = item_type(parent=self)
        self.name = item_name

        if item_type == ItemModel.get_class_from_name("Spreadsheet"):
            sizePolicy = QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
            self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.layout = QtWidgets.QVBoxLayout(self)
        else:
            sizePolicy = QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
            self.layout = QtWidgets.QHBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.item)

        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item.sizePolicy().hasHeightForWidth())
        self.item.setSizePolicy(sizePolicy)

    @property
    def name(self) -> str:
        return self.objectName()

    @name.setter
    def name(self, new_name):
        self.item.setObjectName(new_name)
        self.setObjectName(f"GroupBox_{new_name}")

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
        mime_data.setData('application/x-groupbox-dragged-widget', self.objectName().encode())
        drag.setMimeData(mime_data)

        pixmap = self.grab()
        drag.setPixmap(pixmap)

        local_pos = self.drag_start_position - self.mapToGlobal(self.rect().topLeft())
        drag.setHotSpot(local_pos)

        self.setVisible(False)

        drag.exec(Qt.DropAction.MoveAction)
        self.setVisible(True)

    def clean_up(self):
        self.setParent(None)
        self.item.clean_up()

    def recalculate(self):
        self.item.recalculate()

    def get_dict_data(self) -> Dict[str, Any]:
        data = self.item.get_dict_data()
        data.update({
            'group_box_label': self.label.text(),
        })
        return data


class MyTab(QWidget):
    propertyAdded = pyqtSignal(object)

    def __init__(self, parent, name: str):
        super().__init__(parent)
        self.group_boxes: Set[GroupBox] = set()

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
        if group_box in self.group_boxes:
            raise KeyError(f"group_box already exists.")

        if self.splitter is None:
            raise RuntimeError("Splitter is not initialized.")

        if index == -1 or index >= self.splitter.count():
            self.splitter.addWidget(group_box)
        else:
            self.splitter.insertWidget(index, group_box)

        self.group_boxes.add(group_box)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        from model.Model import Model

        drop_position = event.position().toPoint()
        mime_data = event.mimeData()
        widget_name = None

        if mime_data.data('application/x-groupbox-dragged-widget'):
            widget_name = mime_data.data('application/x-groupbox-dragged-widget').data().decode()

        map_pos = self.splitter.mapFromGlobal(self.mapToGlobal(drop_position))
        widget_under_cursor = self.splitter.childAt(map_pos)

        index = self.splitter.indexOf(
            widget_under_cursor.parent()) if widget_under_cursor else self.splitter.count() - 1
        dragged_widget=Model.find_groupBox(widget_name)
        Model.move_group_box(widget_name,self.name)

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
        widget_to_delete = self.get_GroupBox(index)
        if widget_to_delete is None:
            return

        widget_to_delete.clean_up()
        self.group_boxes.remove(widget_to_delete)

    def clean_up(self):
        from model.Model import Model
        while self.group_boxes:
            self.delete_property(0)
        Model.remove_tab(self.name)

    def context_menu(self, pos):
        index = self.get_index(self.mapToGlobal(pos))

        menu = QMenu()
        add_new_property_action = menu.addAction('Dodaj')

        if index is not None:
            widget = self.get_GroupBox(index)
            name = widget.item.name
            reset_spliter_action = menu.addAction('Przywróć domyślny układ')
            delete_property_action = menu.addAction(f'Usuń {name}')
            edit_property_action = menu.addAction(f'Edytuj {name}')

        action = menu.exec(self.mapToGlobal(pos))
        if action is None:
            return

        if action == add_new_property_action:
            from views.Dialogs.NewPropertyDialog import NewPropertyDialog
            self.property_dialog = NewPropertyDialog(index)
            self.property_dialog.property_added.connect(self.add_property)
        elif action == reset_spliter_action:
            self.reset_spliter()
        elif action == delete_property_action:
            self.delete_property(index)
        elif action == edit_property_action:
            from views.Dialogs.EditPropertyDialog import EditPropertyDialog
            self.edit_property_dialog = EditPropertyDialog(index, widget)
            self.edit_property_dialog.property_edited.connect(self.edit_property)

    def add_property(self, label_text: str, item_name: str, item_type, index: int = 0):
        if item_type is None:
            raise KeyError(f"Missing item_type.")
        tmp = GroupBox(label_text, item_name, item_type, self)

        self.propertyAdded.emit(tmp)
        self.add_group_box(tmp, index)
        return tmp

    def eventFilter(self, a0, a1):
        pass

    def get_index(self, pos):
        closest_index = None
        min_distance = float('inf')

        for i in range(self.splitter.count()):
            widget = self.get_GroupBox(i)

            top_left = widget.mapToGlobal(widget.rect().topLeft())
            bottom_right = widget.mapToGlobal(widget.rect().bottomRight())
            widget_rect = QtCore.QRect(top_left, bottom_right)

            if widget_rect.contains(pos):
                return i

            widget_center = widget_rect.center()
            distance = (pos - widget_center).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                closest_index = i

        return closest_index

    def edit_property(self, label_text, item_name, index):
        widget = self.get_GroupBox(index)
        widget.label.setText(label_text)
        widget.name = item_name

    def get_GroupBox(self, index) -> GroupBox:
        return self.splitter.widget(index)

    def recalculate(self):
        for group_box in self.group_boxes:
            group_box.recalculate()

    def get_dict_data(self) -> Dict[str, Any]:
        group_boxes_data = []
        for group_box in self.group_boxes:
            group_boxes_data.append(group_box.get_dict_data())
        data = {'group_boxes': group_boxes_data,
                'tab_name': self.name,}
        return data


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
        self.setTabBarAutoHide(False)
        self.setObjectName("tabWidget")

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

    def add_new_tab(self, name: str) -> MyTab:
        from model.Model import Model
        my_tab = MyTab(self, name)
        my_tab.propertyAdded.connect(self.propertyAdded.emit)
        self.addTab(my_tab, name)
        Model.add_tab_to_db(my_tab)
        return my_tab

    def delete_tab(self, index: int):
        from model.Model import Model
        if 0 <= index < self.count():
            tab_name = self.tabText(index)
            Model.find_tab(tab_name).clean_up()
            self.removeTab(index)

    def clean_up(self):
        for i in range(self.count()):
            self.delete_tab(0)


