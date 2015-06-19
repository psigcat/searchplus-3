# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/search_plus_dialog_base.ui'
#
# Created: Fri Jun 19 11:53:09 2015
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

class Ui_SearchPlusDialogBase(object):
    def setupUi(self, SearchPlusDialogBase):
        SearchPlusDialogBase.setObjectName(_fromUtf8("SearchPlusDialogBase"))
        SearchPlusDialogBase.resize(400, 300)
        self.button_box = QtGui.QDialogButtonBox(SearchPlusDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))

        self.retranslateUi(SearchPlusDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), SearchPlusDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), SearchPlusDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(SearchPlusDialogBase)

    def retranslateUi(self, SearchPlusDialogBase):
        SearchPlusDialogBase.setWindowTitle(_translate("SearchPlusDialogBase", "searchplus", None))

