# Form implementation generated from reading ui file 'Main_window.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1103, 750)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.PositonsTable = QtWidgets.QTableWidget(parent=self.tab_1)
        self.PositonsTable.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.PositonsTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.PositonsTable.setAlternatingRowColors(True)
        self.PositonsTable.setRowCount(21)
        self.PositonsTable.setColumnCount(6)
        self.PositonsTable.setObjectName("PositonsTable")
        item = QtWidgets.QTableWidgetItem()
        self.PositonsTable.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.PositonsTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.PositonsTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.PositonsTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.PositonsTable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.PositonsTable.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.PositonsTable.setHorizontalHeaderItem(5, item)
        self.PositonsTable.horizontalHeader().setStretchLastSection(True)
        self.PositonsTable.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.PositonsTable)
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.treeWidget = QtWidgets.QTreeWidget(parent=self.tab_2)
        self.treeWidget.setObjectName("treeWidget")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        self.verticalLayout_2.addWidget(self.treeWidget)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget.addTab(self.tab_4, "")
        self.horizontalLayout_3.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1103, 26))
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
        item = self.PositonsTable.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "awd"))
        item = self.PositonsTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "MATERIAŁ"))
        item = self.PositonsTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "OPIS"))
        item = self.PositonsTable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "J.M."))
        item = self.PositonsTable.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "ILOŚĆ"))
        item = self.PositonsTable.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "CENA"))
        item = self.PositonsTable.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "WARTOŚĆ NETTO"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("MainWindow", "Tab 1"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Nazwa"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Wartość"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("MainWindow", "pow.siatki"))
        self.treeWidget.topLevelItem(0).setText(1, _translate("MainWindow", "10.75"))
        self.treeWidget.topLevelItem(1).setText(0, _translate("MainWindow", "Długość budynku w m"))
        self.treeWidget.topLevelItem(1).setText(1, _translate("MainWindow", "6.47"))
        self.treeWidget.topLevelItem(2).setText(0, _translate("MainWindow", "szerokość budynku w m"))
        self.treeWidget.topLevelItem(2).setText(1, _translate("MainWindow", "5.47"))
        self.treeWidget.topLevelItem(3).setText(0, _translate("MainWindow", "pow.fundamentu"))
        self.treeWidget.topLevelItem(3).setText(1, _translate("MainWindow", "dł*szerokość"))
        self.treeWidget.topLevelItem(4).setText(0, _translate("MainWindow", "obwód"))
        self.treeWidget.topLevelItem(4).setText(1, _translate("MainWindow", "(dł+szer)*2"))
        self.treeWidget.topLevelItem(5).setText(0, _translate("MainWindow", "Czy komin?"))
        self.treeWidget.topLevelItem(5).setText(1, _translate("MainWindow", "TAK"))
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Tab 3"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Tab 4"))
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
