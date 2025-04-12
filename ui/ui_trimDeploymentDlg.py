# Form implementation generated from reading ui file 'C:\Users\rick.towler\Work\noaa-afsc-mace\CamtrawlBrowser\ui\trimDeploymentDlg.ui'
#
# Created by: PyQt6 UI code generator 6.6.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_trimDialog(object):
    def setupUi(self, trimDialog):
        trimDialog.setObjectName("trimDialog")
        trimDialog.resize(598, 214)
        font = QtGui.QFont()
        font.setPointSize(10)
        trimDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(trimDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(parent=trimDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.leStart = QtWidgets.QLineEdit(parent=trimDialog)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.leStart.setFont(font)
        self.leStart.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.leStart.setReadOnly(True)
        self.leStart.setObjectName("leStart")
        self.gridLayout.addWidget(self.leStart, 0, 0, 1, 1)
        self.pbSetStart = QtWidgets.QPushButton(parent=trimDialog)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pbSetStart.setFont(font)
        self.pbSetStart.setObjectName("pbSetStart")
        self.gridLayout.addWidget(self.pbSetStart, 1, 0, 1, 1)
        self.leEnd = QtWidgets.QLineEdit(parent=trimDialog)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.leEnd.setFont(font)
        self.leEnd.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.leEnd.setReadOnly(True)
        self.leEnd.setObjectName("leEnd")
        self.gridLayout.addWidget(self.leEnd, 0, 1, 1, 1)
        self.pbSetEnd = QtWidgets.QPushButton(parent=trimDialog)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pbSetEnd.setFont(font)
        self.pbSetEnd.setObjectName("pbSetEnd")
        self.gridLayout.addWidget(self.pbSetEnd, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pbTrim = QtWidgets.QPushButton(parent=trimDialog)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pbTrim.setFont(font)
        self.pbTrim.setObjectName("pbTrim")
        self.horizontalLayout.addWidget(self.pbTrim)
        self.pbCancel = QtWidgets.QPushButton(parent=trimDialog)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pbCancel.setFont(font)
        self.pbCancel.setObjectName("pbCancel")
        self.horizontalLayout.addWidget(self.pbCancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(trimDialog)
        QtCore.QMetaObject.connectSlotsByName(trimDialog)

    def retranslateUi(self, trimDialog):
        _translate = QtCore.QCoreApplication.translate
        trimDialog.setWindowTitle(_translate("trimDialog", "Trim Deployment"))
        self.label.setText(_translate("trimDialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Using the navigation slider and the &quot;Set&quot; buttons, specify the start and end<br/>frames that bound the data you want to keep.</span></p><p align=\"center\"><span style=\" font-size:12pt; font-weight:600; color:#000000;\">All images that fall outside this range will be</span><span style=\" font-size:12pt; font-weight:600; color:#aa0000;\"> permanantly deleted.</span></p></body></html>"))
        self.leStart.setText(_translate("trimDialog", "0"))
        self.pbSetStart.setText(_translate("trimDialog", "Set Start Frame"))
        self.leEnd.setText(_translate("trimDialog", "0"))
        self.pbSetEnd.setText(_translate("trimDialog", "Set End Frame"))
        self.pbTrim.setText(_translate("trimDialog", "Trim Deployment"))
        self.pbCancel.setText(_translate("trimDialog", "Cancel"))
