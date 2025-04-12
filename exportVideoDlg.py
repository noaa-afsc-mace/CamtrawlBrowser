#!/usr/bin/env python

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from ui import ui_setRecordingBoundsDlg

class exportVideoDlg(QDialog, ui_setRecordingBoundsDlg.Ui_recBoundsDialog):

    #  define PyQt Signals
    exportVideo = pyqtSignal(int,int, float, int, bool)

    def __init__(self, slider, enableHudOption=True, parent=None):
        #  initialize the GUI
        super(exportVideoDlg, self).__init__(parent)
        self.setupUi(self)

        self.startFrame = -1
        self.endFrame = -1
        self.leStart.setText('')
        self.leEnd.setText('')
        self.slider = slider
        self.baseRate = 1
        self.enableHudOption = enableHudOption

        #  hide the ShowHUD checkbox if we're not enabling that option
        if not self.enableHudOption:
            self.cbHUD.hide()

        #  connect the signals
        self.pbSetStart.clicked.connect(self.setStart)
        self.pbSetEnd.clicked.connect(self.setEnd)
        self.pbCancel.clicked.connect(self.cancelClicked)
        self.pbExport.clicked.connect(self.exportClicked)
        self.sbSpeed.valueChanged.connect(self.updateEstimatedLen)
        self.sbNFrames.valueChanged.connect(self.updateEstimatedLen)


    def setStart(self):
        val = self.slider.value()
        if ((self.endFrame < 0) or (val < self.endFrame)):
            self.startFrame = val
            self.leStart.setText(str(self.startFrame ))
            self.slider.addTick('Start Video', self.slider.value(), padding=10,
                        thickness=3, color=[20,20,240])
        else:
            QMessageBox.warning(self, 'What?', 'Start frame must be smaller than the end frame')
        self.updateEstimatedLen(None)


    def setEnd(self):
        val = self.slider.value()
        if ((self.startFrame < 0) or (self.startFrame < val)):
            self.endFrame = val
            self.leEnd.setText(str(self.endFrame))
            self.slider.addTick('End Video', self.slider.value(), padding=10,
                        thickness=3, color=[20,20,240])
        else:
            QMessageBox.warning(self, 'What?', 'End frame must be greater than the start frame')
        self.updateEstimatedLen(None)


    def updateEstimatedLen(self, val):

        try:
            totalFrames = int(self.leEnd.text()) - int(self.leStart.text())
            renderedFrames = totalFrames / self.sbNFrames.value()
            fps = self.baseRate * self.sbSpeed.value()
            lenInSecs = renderedFrames / fps
            lenMins = int(lenInSecs // 60)
            lenSecs = int(round(lenInSecs % 60))
            self.leTimeEstimate.setText(f"{lenMins:02d}:{lenSecs:02d}")
        except:
            self.leTimeEstimate.setText("00:00")


    def exportClicked(self):
        try:
            self.startFrame = int(self.leStart.text())
        except:
            QMessageBox.warning(self, 'What?', 'Start frame value is not valid.')
            return
        try:
            self.endFrame = int(self.leEnd.text())
        except:
            QMessageBox.warning(self, 'What?', 'End frame value is not valid.')
            return
        speed = self.sbSpeed.value()
        if self.enableHudOption:
            showHud = self.cbHUD.isChecked()
        else:
            showHud = True
        frameStep = self.sbNFrames.value()

        self.exportVideo.emit(self.startFrame, self.endFrame, speed, frameStep, showHud)
        self.slider.removeTick('Start Video')
        self.slider.removeTick('End Video')
        self.accept()


    def cancelClicked(self):
        self.startFrame = -1
        self.endFrame = -1
        self.leStart.setText('')
        self.leEnd.setText('')
        self.slider.removeTick('Start Video')
        self.slider.removeTick('End Video')
        self.reject()

