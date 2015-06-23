# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/search_plus_dialog_base.ui'
#
# Created: Tue Jun 23 10:18:50 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_dockWidgetBase(object):
    def setupUi(self, dockWidgetBase):
        dockWidgetBase.setObjectName(_fromUtf8("dockWidgetBase"))
        dockWidgetBase.resize(379, 207)
        dockWidgetBase.setLocale(QtCore.QLocale(QtCore.QLocale.Catalan, QtCore.QLocale.Spain))
        dockWidgetBase.setFloating(True)
        dockWidgetBase.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        dockWidgetBase.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea|QtCore.Qt.LeftDockWidgetArea)
        self.contents = QtGui.QWidget()
        self.contents.setObjectName(_fromUtf8("contents"))
        self.tabMain = QtGui.QTabWidget(self.contents)
        self.tabMain.setGeometry(QtCore.QRect(10, 10, 361, 136))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.tabMain.setFont(font)
        self.tabMain.setLocale(QtCore.QLocale(QtCore.QLocale.Catalan, QtCore.QLocale.Spain))
        self.tabMain.setObjectName(_fromUtf8("tabMain"))
        self.tab_1 = QtGui.QWidget()
        self.tab_1.setObjectName(_fromUtf8("tab_1"))
        self.cboStreet = QtGui.QComboBox(self.tab_1)
        self.cboStreet.setGeometry(QtCore.QRect(80, 20, 251, 22))
        self.cboStreet.setEditable(True)
        self.cboStreet.setObjectName(_fromUtf8("cboStreet"))
        self.cboNumber = QtGui.QComboBox(self.tab_1)
        self.cboNumber.setGeometry(QtCore.QRect(80, 60, 71, 22))
        self.cboNumber.setEditable(True)
        self.cboNumber.setObjectName(_fromUtf8("cboNumber"))
        self.lblStreet = QtGui.QLabel(self.tab_1)
        self.lblStreet.setGeometry(QtCore.QRect(10, 20, 46, 21))
        self.lblStreet.setObjectName(_fromUtf8("lblStreet"))
        self.lblNumber = QtGui.QLabel(self.tab_1)
        self.lblNumber.setGeometry(QtCore.QRect(10, 60, 46, 21))
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.tabMain.addTab(self.tab_1, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.lblTopo = QtGui.QLabel(self.tab_2)
        self.lblTopo.setGeometry(QtCore.QRect(10, 10, 341, 31))
        self.lblTopo.setWordWrap(True)
        self.lblTopo.setObjectName(_fromUtf8("lblTopo"))
        self.cboTopo = QtGui.QComboBox(self.tab_2)
        self.cboTopo.setGeometry(QtCore.QRect(10, 50, 191, 22))
        self.cboTopo.setEditable(True)
        self.cboTopo.setObjectName(_fromUtf8("cboTopo"))
        self.tabMain.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.lblType = QtGui.QLabel(self.tab_3)
        self.lblType.setGeometry(QtCore.QRect(10, 20, 46, 21))
        self.lblType.setObjectName(_fromUtf8("lblType"))
        self.cboType = QtGui.QComboBox(self.tab_3)
        self.cboType.setGeometry(QtCore.QRect(80, 20, 201, 22))
        self.cboType.setEditable(True)
        self.cboType.setObjectName(_fromUtf8("cboType"))
        self.cboEquipment = QtGui.QComboBox(self.tab_3)
        self.cboEquipment.setGeometry(QtCore.QRect(80, 60, 201, 22))
        self.cboEquipment.setEditable(True)
        self.cboEquipment.setObjectName(_fromUtf8("cboEquipment"))
        self.lblEquipment = QtGui.QLabel(self.tab_3)
        self.lblEquipment.setGeometry(QtCore.QRect(10, 60, 61, 21))
        self.lblEquipment.setObjectName(_fromUtf8("lblEquipment"))
        self.tabMain.addTab(self.tab_3, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.lblCadastre = QtGui.QLabel(self.tab_4)
        self.lblCadastre.setGeometry(QtCore.QRect(10, 10, 301, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lblCadastre.setFont(font)
        self.lblCadastre.setWordWrap(True)
        self.lblCadastre.setObjectName(_fromUtf8("lblCadastre"))
        self.txtCadastre = QtGui.QLineEdit(self.tab_4)
        self.txtCadastre.setGeometry(QtCore.QRect(10, 50, 191, 20))
        self.txtCadastre.setObjectName(_fromUtf8("txtCadastre"))
        self.tabMain.addTab(self.tab_4, _fromUtf8(""))
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName(_fromUtf8("tab_5"))
        self.lblUTM = QtGui.QLabel(self.tab_5)
        self.lblUTM.setGeometry(QtCore.QRect(10, 10, 281, 31))
        self.lblUTM.setWordWrap(True)
        self.lblUTM.setObjectName(_fromUtf8("lblUTM"))
        self.txtCoordX = QtGui.QLineEdit(self.tab_5)
        self.txtCoordX.setGeometry(QtCore.QRect(60, 50, 113, 20))
        self.txtCoordX.setObjectName(_fromUtf8("txtCoordX"))
        self.txtCoordY = QtGui.QLineEdit(self.tab_5)
        self.txtCoordY.setGeometry(QtCore.QRect(60, 80, 113, 20))
        self.txtCoordY.setObjectName(_fromUtf8("txtCoordY"))
        self.label_8 = QtGui.QLabel(self.tab_5)
        self.label_8.setGeometry(QtCore.QRect(10, 50, 46, 21))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.label_9 = QtGui.QLabel(self.tab_5)
        self.label_9.setGeometry(QtCore.QRect(10, 80, 46, 21))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.tabMain.addTab(self.tab_5, _fromUtf8(""))
        self.button_box = QtGui.QDialogButtonBox(self.contents)
        self.button_box.setGeometry(QtCore.QRect(200, 150, 171, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        dockWidgetBase.setWidget(self.contents)

        self.retranslateUi(dockWidgetBase)
        self.tabMain.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(dockWidgetBase)

    def retranslateUi(self, dockWidgetBase):
        dockWidgetBase.setWindowTitle(_translate("dockWidgetBase", "Cercadors", None))
        self.lblStreet.setText(_translate("dockWidgetBase", "Carrer:", None))
        self.lblNumber.setText(_translate("dockWidgetBase", "Número:", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tab_1), _translate("dockWidgetBase", "Carrerer", None))
        self.lblTopo.setText(_translate("dockWidgetBase", "Desplegueu per seleccionar un topònim; escriviu per constrènyer la cerca (per exemple, \"can\"):", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tab_2), _translate("dockWidgetBase", "Topònims", None))
        self.lblType.setText(_translate("dockWidgetBase", "Tipus:", None))
        self.lblEquipment.setText(_translate("dockWidgetBase", "Equipament:", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tab_3), _translate("dockWidgetBase", "Equipaments", None))
        self.lblCadastre.setText(_translate("dockWidgetBase", "Introduïu la referència cadastral i premeu Acceptar (exemple: \'5123501DF1952S\'):", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tab_4), _translate("dockWidgetBase", "Cadastre", None))
        self.lblUTM.setText(_translate("dockWidgetBase", "Introduïu el parell de coordenades i premeu Acceptar (exemple: X \'415165\', Y \'4592355\'):", None))
        self.label_8.setText(_translate("dockWidgetBase", "X:", None))
        self.label_9.setText(_translate("dockWidgetBase", "Y:", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tab_5), _translate("dockWidgetBase", "UTM", None))

