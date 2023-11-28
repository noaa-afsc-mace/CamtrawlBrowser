

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ui import  ui_CamSelDlg

class CamSelDlg(QDialog, ui_CamSelDlg.Ui_camSelDlg):
    def __init__(self, cameras, parent=None):
        super(CamSelDlg, self).__init__(parent)
        self.setupUi(self)

        #  connect our signals
        self.pbOK.clicked.connect(self.ok)
        self.pbCancel.clicked.connect(self.cancel)
        self.leftBox.currentIndexChanged[int].connect(self.cameraSelected)
        self.rightBox.currentIndexChanged[int].connect(self.cameraSelected)

        #  set up the gui bits
        self.leftCamera = None
        self.rightCamera = None

        self.pbOK.setEnabled(False)
        self.leftBox.addItems(cameras)
        self.rightBox.addItems(cameras)


    @pyqtSlot(int)
    def cameraSelected(self, index):
        #  check if we have sane selections
        if ((self.leftBox.currentIndex() > -1) and (self.rightBox.currentIndex() > -1) and
                (self.leftBox.currentIndex() != self.rightBox.currentIndex())):
            #  different cameras selected, enable the OK button
            self.pbOK.setEnabled(True)
        else:
            #  no cameras or the same cameras selected, don't enable OK
            self.pbOK.setEnabled(False)


    @pyqtSlot()
    def ok(self):
        self.rightCamera = str(self.rightBox.currentText())
        self.leftCamera = str(self.leftBox.currentText())
        self.accept()


    @pyqtSlot()
    def cancel(self):
        self.reject()


    def exit(self):
        self.reject()
