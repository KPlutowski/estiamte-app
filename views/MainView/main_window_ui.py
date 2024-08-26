# Form implementation generated from reading ui file 'resources\designer\Main_window.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(925, 804)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Name_box = QtWidgets.QLineEdit(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Name_box.sizePolicy().hasHeightForWidth())
        self.Name_box.setSizePolicy(sizePolicy)
        self.Name_box.setReadOnly(True)
        self.Name_box.setObjectName("Name_box")
        self.horizontalLayout.addWidget(self.Name_box)
        self.Formula_bar = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.Formula_bar.setObjectName("Formula_bar")
        self.horizontalLayout.addWidget(self.Formula_bar)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabBarAutoHide(True)
        self.tabWidget.setObjectName("tabWidget")
        self.properties_tab = QtWidgets.QWidget()
        self.properties_tab.setObjectName("properties_tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.properties_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(parent=self.properties_tab)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 879, 676))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.formLayout = QtWidgets.QFormLayout(self.scrollAreaWidgetContents_2)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label)
        self.gridArea = DoubleSpinnBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.gridArea.setObjectName("gridArea")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.gridArea)
        self.label_2 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_2)
        self.buildingLength = DoubleSpinnBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.buildingLength.setObjectName("buildingLength")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.buildingLength)
        self.label_3 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_3)
        self.buildingWidth = DoubleSpinnBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.buildingWidth.setObjectName("buildingWidth")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.buildingWidth)
        self.label_4 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_4)
        self.glassQuantity = DoubleSpinnBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.glassQuantity.setObjectName("glassQuantity")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.glassQuantity)
        self.label_5 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_5)
        self.groundFloorWalls = DoubleSpinnBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.groundFloorWalls.setObjectName("groundFloorWalls")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.groundFloorWalls)
        self.label_6 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_6)
        self.roofLength = DoubleSpinnBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.roofLength.setObjectName("roofLength")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.roofLength)
        self.label_19 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_19.setObjectName("label_19")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_19)
        self.firstFloorWalls = DoubleSpinnBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.firstFloorWalls.setObjectName("firstFloorWalls")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.FieldRole, self.firstFloorWalls)
        self.label_7 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_7)
        self.kneeWallHeight = DoubleSpinnBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.kneeWallHeight.setObjectName("kneeWallHeight")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.FieldRole, self.kneeWallHeight)
        self.label_8 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_8)
        self.groundFloorHeight = DoubleSpinnBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.groundFloorHeight.setObjectName("groundFloorHeight")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.ItemRole.FieldRole, self.groundFloorHeight)
        self.attic = CheckBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.attic.setObjectName("attic")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.ItemRole.LabelRole, self.attic)
        self.largeHouse = CheckBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.largeHouse.setObjectName("largeHouse")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.ItemRole.LabelRole, self.largeHouse)
        self.chimney = CheckBoxItem(parent=self.scrollAreaWidgetContents_2)
        self.chimney.setObjectName("chimney")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.ItemRole.LabelRole, self.chimney)
        self.label_9 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_9)
        self.perimeter = LineEditItem(parent=self.scrollAreaWidgetContents_2)
        self.perimeter.setObjectName("perimeter")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.ItemRole.FieldRole, self.perimeter)
        self.label_10 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_10.setObjectName("label_10")
        self.formLayout.setWidget(13, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_10)
        self.foundationArea = LineEditItem(parent=self.scrollAreaWidgetContents_2)
        self.foundationArea.setObjectName("foundationArea")
        self.formLayout.setWidget(13, QtWidgets.QFormLayout.ItemRole.FieldRole, self.foundationArea)
        self.label_11 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_11.setObjectName("label_11")
        self.formLayout.setWidget(14, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_11)
        self.rafterCount = LineEditItem(parent=self.scrollAreaWidgetContents_2)
        self.rafterCount.setEnabled(True)
        self.rafterCount.setObjectName("rafterCount")
        self.formLayout.setWidget(14, QtWidgets.QFormLayout.ItemRole.FieldRole, self.rafterCount)
        self.label_12 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_12.setObjectName("label_12")
        self.formLayout.setWidget(15, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_12)
        self.rafterLength = LineEditItem(parent=self.scrollAreaWidgetContents_2)
        self.rafterLength.setObjectName("rafterLength")
        self.formLayout.setWidget(15, QtWidgets.QFormLayout.ItemRole.FieldRole, self.rafterLength)
        self.label_13 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_13.setObjectName("label_13")
        self.formLayout.setWidget(16, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_13)
        self.groundWallArea = LineEditItem(parent=self.scrollAreaWidgetContents_2)
        self.groundWallArea.setObjectName("groundWallArea")
        self.formLayout.setWidget(16, QtWidgets.QFormLayout.ItemRole.FieldRole, self.groundWallArea)
        self.label_14 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_14.setObjectName("label_14")
        self.formLayout.setWidget(17, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_14)
        self.kneeWallArea = LineEditItem(parent=self.scrollAreaWidgetContents_2)
        self.kneeWallArea.setObjectName("kneeWallArea")
        self.formLayout.setWidget(17, QtWidgets.QFormLayout.ItemRole.FieldRole, self.kneeWallArea)
        self.label_15 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_15.setObjectName("label_15")
        self.formLayout.setWidget(18, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_15)
        self.gableArea = LineEditItem(parent=self.scrollAreaWidgetContents_2)
        self.gableArea.setObjectName("gableArea")
        self.formLayout.setWidget(18, QtWidgets.QFormLayout.ItemRole.FieldRole, self.gableArea)
        self.label_16 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_16.setObjectName("label_16")
        self.formLayout.setWidget(19, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_16)
        self.externalWallArea = LineEditItem(parent=self.scrollAreaWidgetContents_2)
        self.externalWallArea.setObjectName("externalWallArea")
        self.formLayout.setWidget(19, QtWidgets.QFormLayout.ItemRole.FieldRole, self.externalWallArea)
        self.label_17 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_17.setObjectName("label_17")
        self.formLayout.setWidget(20, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_17)
        self.eavesLenght = LineEditItem(parent=self.scrollAreaWidgetContents_2)
        self.eavesLenght.setObjectName("eavesLenght")
        self.formLayout.setWidget(20, QtWidgets.QFormLayout.ItemRole.FieldRole, self.eavesLenght)
        self.label_18 = QtWidgets.QLabel(parent=self.scrollAreaWidgetContents_2)
        self.label_18.setObjectName("label_18")
        self.formLayout.setWidget(21, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_18)
        self.spoutLength = LineEditItem(parent=self.scrollAreaWidgetContents_2)
        self.spoutLength.setObjectName("spoutLength")
        self.formLayout.setWidget(21, QtWidgets.QFormLayout.ItemRole.FieldRole, self.spoutLength)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayout.addWidget(self.scrollArea)
        self.tabWidget.addTab(self.properties_tab, "")
        self.verticalLayout_3.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 925, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuImport = QtWidgets.QMenu(parent=self.menuFile)
        self.menuImport.setObjectName("menuImport")
        self.menuEksport = QtWidgets.QMenu(parent=self.menuFile)
        self.menuEksport.setObjectName("menuEksport")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setEnabled(True)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew = QtGui.QAction(parent=MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionOpen = QtGui.QAction(parent=MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtGui.QAction(parent=MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_as = QtGui.QAction(parent=MainWindow)
        self.actionSave_as.setObjectName("actionSave_as")
        self.actionClose = QtGui.QAction(parent=MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.actionImport_xlm = QtGui.QAction(parent=MainWindow)
        self.actionImport_xlm.setObjectName("actionImport_xlm")
        self.actionExport_xlsx = QtGui.QAction(parent=MainWindow)
        self.actionExport_xlsx.setObjectName("actionExport_xlsx")
        self.actionImportCsv = QtGui.QAction(parent=MainWindow)
        self.actionImportCsv.setObjectName("actionImportCsv")
        self.actionExportCsv = QtGui.QAction(parent=MainWindow)
        self.actionExportCsv.setObjectName("actionExportCsv")
        self.menuImport.addAction(self.actionImport_xlm)
        self.menuImport.addAction(self.actionImportCsv)
        self.menuEksport.addAction(self.actionExport_xlsx)
        self.menuEksport.addAction(self.actionExportCsv)
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.menuImport.menuAction())
        self.menuFile.addAction(self.menuEksport.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Estimatex"))
        self.label.setText(_translate("MainWindow", "Powierzchnia siatki"))
        self.label_2.setText(_translate("MainWindow", "Długość budynku [m]"))
        self.label_3.setText(_translate("MainWindow", "Szerokość budynku [m]"))
        self.label_4.setText(_translate("MainWindow", "Ilość szklanek"))
        self.label_5.setText(_translate("MainWindow", "Ścianki działowe na parterze [mb]"))
        self.label_6.setText(_translate("MainWindow", "Długość połaci"))
        self.label_19.setText(_translate("MainWindow", "Ścianki działowe na piętrze [mb]"))
        self.label_7.setText(_translate("MainWindow", "Wysokość ścianki kolankowej"))
        self.label_8.setText(_translate("MainWindow", "Wysokość ścian parteru"))
        self.attic.setText(_translate("MainWindow", "Czy poddasze użytkowe?"))
        self.largeHouse.setText(_translate("MainWindow", "Czy dom powyżej 70m2?"))
        self.chimney.setText(_translate("MainWindow", "Czy komin?"))
        self.label_9.setText(_translate("MainWindow", "Obwód"))
        self.label_10.setText(_translate("MainWindow", "Powierzchnia Fundamentu"))
        self.label_11.setText(_translate("MainWindow", "Ilość krokwii"))
        self.label_12.setText(_translate("MainWindow", "Długość Krokwii"))
        self.label_13.setText(_translate("MainWindow", "Powierzchnia ściany parteru [m2]"))
        self.label_14.setText(_translate("MainWindow", "Powierzchnia ściany kolankowej [m2]"))
        self.label_15.setText(_translate("MainWindow", "Powierzchnia szczytów [m2]"))
        self.label_16.setText(_translate("MainWindow", "Powierzchnia ścian zewnętrznych [m2]"))
        self.label_17.setText(_translate("MainWindow", "Długość okapu"))
        self.label_18.setText(_translate("MainWindow", "Długość wypustu"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.properties_tab), _translate("MainWindow", "Page"))
        self.menuFile.setTitle(_translate("MainWindow", "Plik"))
        self.menuImport.setTitle(_translate("MainWindow", "Import"))
        self.menuEksport.setTitle(_translate("MainWindow", "Eksport"))
        self.actionNew.setText(_translate("MainWindow", "Nowy..."))
        self.actionNew.setIconText(_translate("MainWindow", "Nowy kosztorys"))
        self.actionNew.setToolTip(_translate("MainWindow", "Nowy kosztorys"))
        self.actionNew.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionOpen.setText(_translate("MainWindow", "Otwórz..."))
        self.actionOpen.setIconText(_translate("MainWindow", "Otwórz kosztorys"))
        self.actionOpen.setToolTip(_translate("MainWindow", "Otwórz kosztorys"))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave.setText(_translate("MainWindow", "Zapisz..."))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_as.setText(_translate("MainWindow", "Zapisz jako..."))
        self.actionSave_as.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionClose.setText(_translate("MainWindow", "Zamknij"))
        self.actionClose.setShortcut(_translate("MainWindow", "Ctrl+F4"))
        self.actionImport_xlm.setText(_translate("MainWindow", "Kosztorys (*.xml)"))
        self.actionExport_xlsx.setText(_translate("MainWindow", "Plik XLSX"))
        self.actionImportCsv.setText(_translate("MainWindow", "*.csv"))
        self.actionExportCsv.setText(_translate("MainWindow", "*.csv"))
from model.CheckBoxItem import CheckBoxItem
from model.DoubleSpinnBoxItem import DoubleSpinnBoxItem
from model.LineEditItem import LineEditItem
