from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QScrollArea


class PropertiesWidget(QWidget):
    def __init__(self, parent,name):
        super().__init__(parent)
        self.name = name

        self.scroll_area = QScrollArea(parent)
        self.scroll_area.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.scroll_area.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 818, 626))
        self.scroll_vertical_layout = QVBoxLayout(self.scrollAreaWidgetContents)

        self.scroll_area.setWidget(self.scrollAreaWidgetContents)
        parent.layout().addWidget(self.scroll_area)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)


class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        self.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabBarAutoHide(True)
        self.setObjectName("tabWidget")

    def add_tab(self, name) -> QWidget:
        new_tab = QtWidgets.QWidget()
        new_tab.setObjectName(f"tab_{name}")
        new_tab.setAcceptDrops(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(new_tab)
        self.addTab(new_tab, name)
        return new_tab

    def get_tab_by_name(self, name: str):
        for i in range(self.count()):
            widget = self.widget(i)
            if widget.objectName() == name:
                return widget.children()[0]
        return None


