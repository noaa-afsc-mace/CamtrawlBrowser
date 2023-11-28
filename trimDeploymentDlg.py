#!/usr/bin/env python

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from ui import ui_trimDeploymentDlg

class trimDeploymentDlg(QDialog, ui_trimDeploymentDlg.Ui_trimDialog):

    #  define PyQt Signals
    trimDeployment = pyqtSignal(int,int)

    def __init__(self, slider, parent=None):
        #  initialize the GUI
        super(trimDeploymentDlg, self).__init__(parent)
        self.setupUi(self)

        self.startFrame = -1
        self.endFrame = -1
        self.leStart.setText('')
        self.leEnd.setText('')
        self.slider = slider

        #  connect the signals
        self.pbSetStart.clicked.connect(self.setStart)
        self.pbSetEnd.clicked.connect(self.setEnd)
        self.pbCancel.clicked.connect(self.cancelClicked)
        self.pbTrim.clicked.connect(self.trimClicked)


    def setStart(self):
        val = self.slider.value()
        if ((self.endFrame < 0) or (val < self.endFrame)):
            self.startFrame = val
            self.leStart.setText(str(self.startFrame ))
            self.slider.addTick('startTrim', self.slider.value(), padding=10,
                        thickness=3, color=[240,10,10])
        else:
            QMessageBox.warning(self, 'What?', 'Start frame must be smaller than the end frame')


    def setEnd(self):
        val = self.slider.value()
        if ((self.startFrame < 0) or (self.startFrame < val)):
            self.endFrame = val
            self.leEnd.setText(str(self.endFrame))
            self.slider.addTick('endTrim', self.slider.value(), padding=10,
                        thickness=3, color=[240,10,10])
        else:
            QMessageBox.warning(self, 'What?', 'End frame must be greater than the start frame')


    def trimClicked(self):
        self.startFrame = int(self.leStart.text())
        self.endFrame = int(self.leEnd.text())
        self.trimDeployment.emit(self.startFrame, self.endFrame)
        self.slider.removeTick('startTrim')
        self.slider.removeTick('endTrim')
        self.accept()


    def cancelClicked(self):
        self.startFrame = -1
        self.endFrame = -1
        self.leStart.setText('')
        self.leEnd.setText('')
        self.slider.removeTick('startTrim')
        self.slider.removeTick('endTrim')
        self.reject()

