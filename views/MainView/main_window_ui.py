# Form implementation generated from reading ui file 'resources\designer\MainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(864, 819)
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
        self.tabWidget = TabWidget(parent=self.centralwidget)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabBarAutoHide(True)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout_3.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 864, 26))
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
        self.actionExport_pdf = QtGui.QAction(parent=MainWindow)
        self.actionExport_pdf.setObjectName("actionExport_pdf")
        self.actionExport_xml = QtGui.QAction(parent=MainWindow)
        self.actionExport_xml.setObjectName("actionExport_xml")
        self.actionImport_xlsx = QtGui.QAction(parent=MainWindow)
        self.actionImport_xlsx.setObjectName("actionImport_xlsx")
        self.menuImport.addAction(self.actionImport_xlm)
        self.menuImport.addAction(self.actionImport_xlsx)
        self.menuEksport.addAction(self.actionExport_xlsx)
        self.menuEksport.addAction(self.actionExport_pdf)
        self.menuEksport.addAction(self.actionExport_xml)
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
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Estimatex"))
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
        self.actionExport_pdf.setText(_translate("MainWindow", "Plik PDF"))
        self.actionExport_xml.setText(_translate("MainWindow", "Plik xml"))
        self.actionImport_xlsx.setText(_translate("MainWindow", ".XLSX"))
from resources.TabWidget import TabWidget
