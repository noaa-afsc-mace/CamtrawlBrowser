# Form implementation generated from reading ui file 'C:\Users\rick.towler\Work\noaa-afsc-mace\CamtrawlBrowser\ui\CamSelDlg.ui'
#
# Created by: PyQt6 UI code generator 6.6.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_camSelDlg(object):
    def setupUi(self, camSelDlg):
        camSelDlg.setObjectName("camSelDlg")
        camSelDlg.resize(586, 137)
        self.verticalLayout = QtWidgets.QVBoxLayout(camSelDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.formLayout.setVerticalSpacing(12)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(parent=camSelDlg)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label)
        self.leftBox = QtWidgets.QComboBox(parent=camSelDlg)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.leftBox.setFont(font)
        self.leftBox.setObjectName("leftBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.leftBox)
        self.label_2 = QtWidgets.QLabel(parent=camSelDlg)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_2)
        self.rightBox = QtWidgets.QComboBox(parent=camSelDlg)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.rightBox.setFont(font)
        self.rightBox.setObjectName("rightBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.rightBox)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pbOK = QtWidgets.QPushButton(parent=camSelDlg)
        self.pbOK.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pbOK.setFont(font)
        self.pbOK.setObjectName("pbOK")
        self.horizontalLayout.addWidget(self.pbOK)
        self.pbCancel = QtWidgets.QPushButton(parent=camSelDlg)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pbCancel.setFont(font)
        self.pbCancel.setObjectName("pbCancel")
        self.horizontalLayout.addWidget(self.pbCancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(camSelDlg)
        QtCore.QMetaObject.connectSlotsByName(camSelDlg)

    def retranslateUi(self, camSelDlg):
        _translate = QtCore.QCoreApplication.translate
        camSelDlg.setWindowTitle(_translate("camSelDlg", "Specify Camera Mouting Positions"))
        self.label.setText(_translate("camSelDlg", "Left Camera"))
        self.label_2.setText(_translate("camSelDlg", "Right Camera"))
        self.pbOK.setText(_translate("camSelDlg", "OK"))
        self.pbCancel.setText(_translate("camSelDlg", "Cancel"))
