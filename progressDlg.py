
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from ui import  ui_progressDlg


class progressDlg(QDialog, ui_progressDlg.Ui_progressDlg):


    #  define PyQt Signals
    cancel = pyqtSignal()

    def __init__(self, parent=None):
        super(progressDlg, self).__init__(parent)
        self.setupUi(self)

        self.pbCancel.clicked.connect(self.cancelExport)


    def setText(self, text):

        self.label.setText(str(text))


    def updateProgress(self, progress):

        progress = round(progress)

        if progress > 100:
            progress = 100
        elif progress < 0:
            progress = 0

        self.progressBar.setValue(progress)


    def cancelExport(self):

        ok = QMessageBox.question(self, 'Stop Export?',
                'Are you sure you want to stop exporting the video?')
        if ok:
            self.cancel.emit()
