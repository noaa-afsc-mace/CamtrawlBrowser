#!/usr/bin/env python

import sys
import os
import pickle
import shutil
import datetime
import traceback
import functools
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from ui import ui_CamtrawlBrowser
import trimDeploymentDlg
import CamtrawlMetadata
import camseldlg

class CamtrawlBrowser(QMainWindow, ui_CamtrawlBrowser.Ui_CamtrawlBrowser):

    def __init__(self, resetWindowPosition=False, parent=None):
        super(CamtrawlBrowser, self).__init__(parent)
        self.setupUi(self)

        #  Set some default properties
        self.enhanceCalExportImages = True
        self.leftDateTimeLabel = None
        self.rightDateTimeLabel = None
        self.leftCamera = None
        self.rightCamera = None
        self.lastNumberLoaded = -1
        self.maxQueuedImages = 2
        self.leftImageQueue = []
        self.rightImageQueue = []

        #  create an instance of the CamtrawlMetadata class to handle reading our metadata database
        self.metadata = CamtrawlMetadata.CamTrawlMetadata()

        #  create an instance of the trim deployment dialog
        self.trimDialog = trimDeploymentDlg.trimDeploymentDlg(self.imageSlider, parent=self)
        self.trimDialog.trimDeployment[int,int].connect(self.trimDeployment)

        #  connect the QImageViewer key press signals
        self.gvLeft.keyPress.connect(self.imageKeyPressEvent)
        self.gvRight.keyPress.connect(self.imageKeyPressEvent)

        #  connect the GUI signals and slots
        self.actionExit.triggered.connect(self.close)
        self.actionLoad.triggered.connect(self.openDeployment)
        self.actionPlotVAT.triggered.connect(self.plotSystemVoltageTemp)
        self.actionPlotDepth.triggered.connect(self.plotDepthProfile)
        #self.centralwidget.keyPressed.connect(self.keyPressEvent)
        self.pbMarkCurrent.clicked.connect(self.markPosition)
        self.pbPreviousMark.clicked.connect(self.navigateToMark)
        self.pbNextMark.clicked.connect(self.navigateToMark)
        self.pbDeleteMark.clicked.connect(self.removeMark)
        self.pbExportImage.clicked.connect(self.exportImages)
        self.exportBtn.clicked.connect(self.exportData)
        self.pbTrim.clicked.connect(self.showTrimDeployment)
        self.pbExForCal.clicked.connect(self.exportForCal)
        self.playBtn.clicked.connect(self.play)
        self.playSpeedDial.valueChanged[int].connect(self.speedSet)
        self.imageSlider.valueChanged[int].connect(self.changeImage)
        #self.imageSlider.keyPressEvent.connect(self.changeImage)

        #  restore the application state
        self.appSettings = QSettings('afsc.noaa.gov', 'CamtrawlBrowser')
        position = self.appSettings.value('winposition', QPoint(10,10))
        size = self.appSettings.value('winsize', QSize(1000,700))

        if not resetWindowPosition:
            #  check the current position and size to make sure the app is on the screen
            position, size = self.checkWindowLocation(position, size)

            #  now move and resize the window
            self.move(position)
            self.resize(size)

        self.dataDir = self.appSettings.value('datadir', QDir.home().path())
        self.copyDir = self.appSettings.value('copydir', QDir.home().path())

        #  set a couple of button styles for the playback button
        self.green = "QPushButton { background-color: rgb(77,223,77)}"
        self.gray = "QPushButton { background-color: rgb(150,150,150)}"

        #  set initial properties of the GUI elements
        self.imageSlider.setEnabled(False)
        self.depth.setText('')
        self.pitch.setText('')
        self.yaw.setText('')
        self.roll.setText('')
        self.playBtn.setStyleSheet(self.gray)
        self.playSpeedDial.setWrapping(False)

        #  disable the GUI elements
        self.imageSlider.setEnabled(False)
        self.actionPlotVAT.setEnabled(False)
        self.actionPlotDepth.setEnabled(False)
        self.exportBtn.setEnabled(False)
        self.pbTrim.setEnabled(False)
        self.pbExportImage.setEnabled(False)
        self.pbExForCal.setEnabled(False)
        self.gbPlay.setEnabled(False)
        self.gbMarks.setEnabled(False)

        #  set the base directory path - this is the full path to this application
        self.baseDir = functools.reduce(lambda l,r: l + os.path.sep + r,
                os.path.dirname(os.path.realpath(__file__)).split(os.path.sep))
        try:
            self.setWindowIcon(QIcon(self.baseDir + os.sep + 'resources/fish.png'))
        except:
            pass

        #  create the playback timer
        self.playTimer = QTimer(self)
        self.playTimer.timeout.connect(self.moveSlider)

        #  create the queue process timer
        self.queueTimer = QTimer(self)
        self.queueTimer.timeout.connect(self.processQueue)
        self.queueTimer.start(10)

        #  start a timer event to load the help image
        helpTimer = QTimer(self)
        helpTimer.setSingleShot(True)
        helpTimer.timeout.connect(self.showHelpImage)
        helpTimer.start(250)


    def showHelpImage(self):

        #  clear the viewers
        self.gvLeft.clearViewer()
        self.leftCamLabel = []
        self.gvRight.clearViewer()
        self.rightCamLabel = []

        #  load the help images
        self.gvLeft.setImageFromFile(self.baseDir + os.sep + 'resources/help.png')
        self.gvRight.setImageFromFile(self.baseDir + os.sep + 'resources/help.png')
        self.gvLeft.fillExtent()
        self.gvRight.fillExtent()


    def toFloat(self, val):
        try:
            f = float(val)
        except:
            f = np.nan

        return f


    def plotDepthProfile(self):
        '''
        plotDepthProfile plots the camera systems depth vs deployment time
        '''

        #  extract time, pitch, roll, depth, and temp from sensorData
        depth = []
        temperature = []
        pitch = []
        roll = []
        time = []
        for i in self.metadata.sensorData['CTControl']['$OHPR'].keys():
            #  split the sensor string
            parts = self.metadata.sensorData['CTControl']['$OHPR'][i].split(',')
            #  get the time
            time.append(self.metadata.sensorData['utc_time'][i])
            #  convert temp and voltage to a float and store
            depth.append(self.toFloat(parts[5]))
            temperature.append(self.toFloat(parts[4]))
            pitch.append(self.toFloat(parts[2]))
            roll.append(self.toFloat(parts[3]))

        #  set the plot style
        mpl.style.use('seaborn-v0_8')
        #  create a figure and sxes
        fig, ax = plt.subplots()
        scale = 20.0

        #  plot just depth, or if we have temp, depth and temp
        if (temperature[0] > -900):
            #  we have both depth and temp
            p = ax.scatter(time, depth, s=scale, c=temperature, cmap=plt.get_cmap('viridis'))
            fig.colorbar(p)
            ax.set_title('System Depth and Water Temperature')
        else:
            #  no temp data - must be analog pressure sensor
            ax.scatter(time, depth, s=scale,c='C1')
            ax.set_title('System Depth')

        #  set the x axis limts
        padding = datetime.timedelta(seconds=120)
        ax.set_xlim(time[0] - padding, time[-1] + padding)

        #  invert the Y axis
        ax.invert_yaxis()

        #  set labels and title
        ax.set_ylabel('Depth (m)')
        ax.set_xlabel('Time')

        #  fancy up the x labels
        fig.autofmt_xdate()

        #  add a figure title
        fig.suptitle('Camera Deployment ' + str(self.deployment.text()), fontsize=16)

        #  show the plot
        plt.show()


    def plotSystemVoltageTemp(self):
        '''
        plotSystemVoltageTemp plots camtrawl system voltage and temperature data
        vs deployment time.
        '''

        #  extract the system voltage and IMU temp
        batteryVoltage = []
        imuTemp = []
        batteryTime = []
        for i in range(0, len(self.metadata.asyncData['CTControl']['$CTSV']['utc_time'])):
            #  split the sensor string
            parts = self.metadata.asyncData['CTControl']['$CTSV']['data'][i].split(',')
            #  get the time
            batteryTime.append(self.metadata.asyncData['CTControl']['$CTSV']['utc_time'][i])
            #  convert temp and voltage to a float and store
            batteryVoltage.append(self.toFloat(parts[2]))
            imuTemp.append(self.toFloat(parts[3]))

        #  get the camera voltage and temp
        cameraVoltage = {}
        cameraTemp = {}
        cameraTime = {}
        #  generate dicts keyed by camera to hold temp, voltage, and time
        cameras = list(self.metadata.cameras.keys())
        for c in cameras:
            cameraVoltage[c] = []
            cameraTemp[c] = []
            cameraTime[c] = []

        #  check if we have camera voltages available
        if 'Camera' in self.metadata.asyncData:
            #  and populate these lists
            for i in range(0, len(self.metadata.asyncData['Camera']['$CTCS']['utc_time'])):
                #  split the sensor string
                parts = self.metadata.asyncData['Camera']['$CTCS']['data'][i].split(',')
                #  get the time
                cameraTime[parts[1]].append(self.metadata.asyncData['Camera']['$CTCS']['utc_time'][i])
                #  convert temp and voltage to a float and store
                cameraVoltage[parts[1]].append(self.toFloat(parts[2][1:-1]))
                cameraTemp[parts[1]].append(self.toFloat(parts[4]))

        mpl.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(nrows=2)

        #  plot the voltages
        for i in range(0,len(cameras)):
            camera = cameras[i]
            color = 'C' + str(i)
            axes[0].plot(cameraTime[camera],cameraVoltage[camera],color, label=camera)
        axes[0].plot(batteryTime,batteryVoltage,'C5', label='System')
        axes[0].set(xlabel='Time', ylabel='Voltage (V)',
            title='System Voltages')
        axes[0].legend()

        #  plot the temps
        for i in range(len(cameras)):
            camera = cameras[i]
            color = 'C' + str(i)
            axes[1].plot(cameraTime[camera],cameraTemp[camera],color, label=camera)
        axes[1].plot(batteryTime,imuTemp,'C5', label='System')
        axes[1].set(xlabel='Time', ylabel='Temperature (C)',
            title='System Temperatures')
        axes[1].legend()

        #  fancy up the x labels
        fig.autofmt_xdate()

        #  add a figure title
        fig.suptitle('Camera Deployment ' + str(self.deployment.text()), fontsize=16)

        #  show the plot
        plt.show()


    def showTrimDeployment(self):

        self.trimDialog.show()


    def trimDeployment(self, startFrame, endFrame):

        ok = QMessageBox.question(self, 'Trim?', '<span style=" font-weight:600; color:#000000;">' +
                'Are you REALLY sure you want to trim this deployment? <span style=" font-weight:600;' +
                'color:#E00000;">This will PERMANANTLY delete ALL images before frame ' +
                str(startFrame) + ' and after frame ' + str(endFrame) + '!',
                QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel)

        if (ok == QMessageBox.StandardButton.Ok):

            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            #  set the clipped images to "discarded" in the metadata database
            self.statusBar.showMessage('Modifying metadata database...')
            self.metadata.setDiscarded(self.metadata.startImage, startFrame - 1)
            self.metadata.setDiscarded(endFrame + 1, self.metadata.endImage)

            #  delete the images
            self.statusBar.showMessage('Deleting trimmed images...')
            self.metadata.deleteDiscardedImages()

            #  reload the newly modified metadata
            self.statusBar.showMessage('Querying new metadata database...')
            self.metadata.query()

            #  and re-load the newly modified deployment
            self.loadDeployment()

            self.statusBar.clearMessage()
            QApplication.restoreOverrideCursor()


    def closeDeployment(self):
        """
        closeDeployment takes care of updating the metadata database with the
        image adjustments.
        """

        #  store the image adjustment parameters in the deployment metadata database
        if (self.leftCamera):
            leftAdjustments = self.gvLeft.image.getParameters()
            leftAdjustments = pickle.dumps(leftAdjustments,2)
            self.metadata.setImageAdjustments(self.leftCamera, leftAdjustments)
        if (self.rightCamera):
            rightAdjustments = self.gvRight.image.getParameters()
            rightAdjustments = pickle.dumps(rightAdjustments,2)
            self.metadata.setImageAdjustments(self.rightCamera, rightAdjustments)

        #  close our metadata file
        self.metadata.close()


    def closeEvent(self, event):
        """
        closeEvent is called when the application is closed and performs some
        basic clean up
        """

        #  stop the timers
        self.playTimer.stop()

        #  store the image adjustment parameters in the deployment metadata database
        self.closeDeployment()

        #  store the application size and position
        self.appSettings.setValue('winposition', self.pos())
        self.appSettings.setValue('winsize', self.size())

        event.accept()


    def resizeEvent(self, event):
        """
        resizeEvent is called when the GUI is resized
        """

        #  Scale the image to fill the the image widget when we resize.
        #  This is a bit heavy handed, it will reset the zoom on resize,
        #  but we want the image to scale when we resize and dealing with
        #  the details of resizing when zoomed is a headache.
        self.gvLeft.fillExtent()
        self.gvRight.fillExtent()


    def openDeployment(self):
        """
        openDeployment is called when the user clicks on File->Open...
        """

        #  present the user with the directory selection dialog
        dirDlg = QFileDialog(self)
        dirName = dirDlg.getExistingDirectory(self, 'Select Deployment Directory',
                    self.dataDir, QFileDialog.Option.ShowDirsOnly)

        if (dirName != ''):
            #  update the application settings with the data directory
            self.appSettings.setValue('datadir', dirName)
            self.dataDir = dirName

            #  if we have a deployment open, make sure we update the image settings
            #  in the metadata file before closing it.
            if (self.rightCamera or self.leftCamera):
                self.closeDeployment()

            #  clear the viewers and reset some other vars/props
            self.rightCamera = None
            self.leftCamera = None
            self.gvLeft.clearViewer()
            self.gvLeft.removeAllHudItems()
            self.gvLeft.resetTransform()
            self.leftCamLabel = []
            self.leftImageQueue = []
            self.gvRight.clearViewer()
            self.gvRight.removeAllHudItems()
            self.gvRight.resetTransform()
            self.rightCamLabel = []
            self.rightImageQueue = []
            self.lastNumberLoaded = -1

            #  disable the GUI elements
            self.imageSlider.setEnabled(False)
            self.actionPlotVAT.setEnabled(False)
            self.actionPlotDepth.setEnabled(False)
            self.exportBtn.setEnabled(False)
            self.pbTrim.setEnabled(False)
            self.pbExportImage.setEnabled(False)
            self.pbExForCal.setEnabled(False)
            self.gbPlay.setEnabled(False)
            self.gbMarks.setEnabled(False)

            try:
                #  read the image metadata
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                self.statusBar.showMessage('Reading metadata...')
                self.metadata.open(self.dataDir)
                self.metadata.query()
                self.metadata.updateDeployentMetadata()

                #  and load the deployment
                self.loadDeployment()
                QApplication.restoreOverrideCursor()

            except:
                #  no metadata database present, can't work with this
                QApplication.restoreOverrideCursor()
                self.statusBar.clearMessage()
                QMessageBox.critical(self, "That's unpossible!", "Unable to open the deployment's " +
                        "metadata database. Did you select the correct directory? "+
                        "Are you sure this is a CamTrawl brand deployment package?")
                return


    def exportForCal(self):
        '''
        exportForCal copies all of the images with marks to a new folder. The files are
        renamed folloing a simple convention to make it easier to load into your calibraiton
        program of choice.
        '''

        def exportCalImage(viewObj, camName, frame, imagePrefix, enhance):

            imageName = self.metadata.imageData[camName][frame][2]
            sourcePath = self.dataDir + os.path.sep + "images" + os.path.sep + \
                    camName + os.path.sep + imageName + '.' + imageExt
            destPath = (exportDir + os.path.sep + imagePrefix + str(frameCount) + '.' + imageExt)

            if enhance:
                #  load the image using the viewer which will apply enhancements if enabled
                viewObj.setImageFromFile(sourcePath)
                viewObj.saveImage(destPath)
            else:
                #  we're not applying enhancements so just copy the file
                shutil.copyfile(sourcePath, destPath)


        #  hard code the image extension for now
        imageExt = 'jpg'

        ok = QMessageBox.information(self, 'Export for Calibration', "Export for calibration " +
                "saves copies of all images with marks. The image names are simplified " +
                "along the way making them easier to load into your calibration tool " +
                "of choice. The files are written to a folder named 'Exported for Cal' " +
                "in the images folder for this deployment. Do you want to export " +
                "your marked files?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)

        if (ok == QMessageBox.StandardButton.No):
            return

        #  update the metadata (probably don't need to do this)
        self.metadata.query()

        #  get all of the frames with marks
        frames = self.metadata.marks.keys()

        #  create the export path
        exportDir = str(self.dataDir + "/images/ExportForCal")

        #  check for and delete existing export directory
        if (os.path.isdir(exportDir)):
            ok = QMessageBox.warning(self, 'Export Directory Exists', "A calibration " +
                    "export directory already exists. Do you want to replace it? All exising " +
                    "images will be deleted!", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)

            if (ok == QMessageBox.StandardButton.No):
                return

            try:
                if (os.path.isdir(exportDir)):
                    shutil.rmtree(exportDir)
            except:
                ok = QMessageBox.critical(self, 'Error deleting export directory',
                        "Unable to delete existing export directory. Export aborted.")
                return

        #  create the export directory
        try:
            os.mkdir(exportDir)
        except:
            ok = QMessageBox.critical(self, 'Error creating export directory',
                        "Unable to create export directory. Export aborted.")
            return

        #  now export the images
        frameCount = 1
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        for frame in frames:
            self.statusBar.showMessage('Exporting calibration image ' + str(frameCount) +
                    ' of ' + str(len(frames)))

            try:
                #  export the left image
                exportCalImage(self.gvLeft, self.leftCamera, frame, 'L', self.enhanceCalExportImages)
                #  and then the right
                exportCalImage(self.gvRight, self.rightCamera, frame, 'R', self.enhanceCalExportImages)

            except:
                #  something went wrong - throw up a traceback
                tracebackText = traceback.format_exception(*sys.exc_info())
                tracebackText = '\n'.join(tracebackText)
                QMessageBox.error(self, "Fatal", tracebackText)
                QMessageBox.information(self, 'Export Aborted', "Export aborted due to error.")
                QApplication.restoreOverrideCursor()
                self.statusBar.showMessage('')
                return

            #  increment the exported frame counter
            frameCount += 1

            QApplication.processEvents()

        #  reset the GUI and inform user we're done
        QApplication.restoreOverrideCursor()
        self.statusBar.showMessage('')
        QMessageBox.information(self, 'Export Complete!', "Export complete.")


    def loadDeployment(self):

        #  check if we have a default camera arrangement
        self.cameras = self.metadata.cameras.keys()
        for camera in self.cameras:
            if (self.metadata.cameras[camera]['label'].lower() == 'right'):
                self.rightCamera = camera
            if (self.metadata.cameras[camera]['label'].lower() == 'left'):
                self.leftCamera = camera

        #  at least one of the cameras wasn't labeled so display the selection dialog
        if (self.rightCamera == None) or (self.leftCamera == None):
            dlg = camseldlg.CamSelDlg(self.cameras)
            if dlg.exec_():
                self.leftCamera = dlg.leftCamera
                self.rightCamera = dlg.rightCamera
            else:
                return

        #  try to get the camera orientations
        #  Newer versions of acquisition save the image already rotated so we don't
        #  need to rotate here and if we do, it results in a double rotation. It is
        #  possible we will need to rotate images in the future, but we will need to
        #  come up with a different way to do this because the orientation column in
        #  the metadata is just informing the user that the saved imaegs are rotated.
        #  It does not mean they *need* to be rotated.
#        try:
#            self.gvRight.setRotation(self.metadata.cameras[self.rightCamera]['orientation'])
#        except:
#            #  no orientation data available for this camera
#            pass
#        try:
#            self.gvLeft.setRotation(self.metadata.cameras[self.leftCamera]['orientation'])
#        except:
#            #  no orientation data available for this camera
#            pass

        #  try to get the stored image adjustment parameters for these cameras
        adjustments = self.metadata.getImageAdjustments(self.leftCamera)
        if (adjustments):
            adjustments = pickle.loads(adjustments)
            self.gvLeft.image.setParameters(adjustments)
        adjustments = self.metadata.getImageAdjustments(self.rightCamera)
        if (adjustments):
            adjustments = pickle.loads(adjustments)
            self.gvRight.image.setParameters(adjustments)

        #  update the GUI elements
        self.deployment.setText(self.dataDir.split(os.path.sep)[-1])
        self.minFrame.setText(str(self.metadata.startImage))
        self.maxFrame.setText(str(self.metadata.endImage))
        self.imageSlider.setMinimum(0)
        self.imageSlider.setMaximum(len(self.metadata.imageNumbers) - 1)
        self.imageSlider.setSingleStep(1)
        self.imageSlider.setPageStep(10)
        self.imageSlider.setValue(0)
        self.imageSlider.setEnabled(True)
        self.actionPlotVAT.setEnabled(True)
        self.actionPlotDepth.setEnabled(True)
        self.exportBtn.setEnabled(True)
        self.pbTrim.setEnabled(True)
        self.pbExportImage.setEnabled(True)
        self.pbExForCal.setEnabled(True)
        self.gbPlay.setEnabled(True)
        self.gbMarks.setEnabled(True)

        #  add the mark ticks to the scrollbar
        self.imageSlider.removeAllTicks()
        for markLoc in self.metadata.marks:
            markIdx = self.metadata.imageNumbers.index(markLoc)
            self.imageSlider.addTick(str(markLoc), markIdx, padding=10,
                    thickness=3, color=[10,10,240])

        #  set the top label on the HUD
        self.gvLeft.setName(self.leftCamera)
        self.leftCamLabel = self.gvLeft.addHudText(QPointF(0.5,0.001),
                self.leftCamera, size=11, color=[0,250,0], alpha=150,
                halign='center', valign='top')

        self.gvRight.setName(self.rightCamera)
        self.rightCamLabel = self.gvRight.addHudText(QPointF(0.5,0.001),
                self.rightCamera, size=11, color=[0,250,0], alpha=150,
                halign='center', valign='top')

        self.changeImage()
        self.statusBar.clearMessage()
        QApplication.restoreOverrideCursor()


    def markPosition(self):
        #  check if this was a shift-click which selects the image for cal
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ShiftModifier:
            description = 'Selected for Calibration'
            self.marksDescription.setText(description)
        else:
            if self.marksDescription.text()=='':
                QMessageBox.critical(self, 'Error', 'Please enter mark description.')
                return
            else:
                description = self.marksDescription.text()

        #  add the mark
        imageIndex = self.imageSlider.value()
        imageNumber = self.metadata.imageNumbers[imageIndex]
        self.metadata.createMark(imageNumber, description)
        self.imageSlider.addTick(str(imageNumber), imageIndex, padding=10,
                    thickness=3, color=[10,10,240])


    def removeMark(self):
        ok = QMessageBox.warning(self, "WARNING", "Sure you want to delete this mark?",
                QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
        if (ok == QMessageBox.StandardButton.Yes):
            imageIndex = self.imageSlider.value()
            imageNumber = self.metadata.imageNumbers[imageIndex]
            self.metadata.removeMark(imageNumber)
            self.imageSlider.removeTick(str(imageNumber))
            self.marksDescription.setText('')


    def navigateToMark(self):
        imageIndex = self.imageSlider.value()
        imageNumber = self.metadata.imageNumbers[imageIndex]
        if self.sender()==self.pbNextMark:
            (frame, text)=self.metadata.findNextMark(imageNumber)
        else:
            (frame, text)=self.metadata.findPreviousMark(imageNumber)
        if (frame != None):
            nextIndex = self.metadata.imageNumbers.index(frame)
            self.imageSlider.setValue(nextIndex)
            self.marksDescription.setText(text)


    def imageKeyPressEvent(self, imgObj, ev):
        '''
        imageKeyPressEvent sends key presses within our QImageView/QEchogramView objects
        to our keypress event handler for the central widget. At this point
        QImageView/QEchogramView  has already handled their internal key press handling.

        '''
        self.keyPressEvent(ev)


    def keyPressEvent(self, ev):
        """
        keyPressEvent handles application keyboard input and responds to key presses
        """
        currentIndex = self.imageSlider.value()

        #nextIndex = currentIndex
        if (ev.key() == Qt.Key.Key_Right):
            #  increment slider one image
            self.imageSlider.setValue(currentIndex + 1)
        elif (ev.key() == Qt.Key.Key_Left):
            #  decrement slider one image
            self.imageSlider.setValue(currentIndex - 1)
        elif (ev.key() == Qt.Key.Key_Up):
            #  increment slider ten images
            self.imageSlider.setValue(currentIndex + 10)
        elif (ev.key() == Qt.Key.Key_Down):
            #  decrement slider ten images
            self.imageSlider.setValue(currentIndex - 10)


    def processQueue(self):

        if (len(self.leftImageQueue) > 0):
            #  get the next left image number and path
            number, pathLeft = self.leftImageQueue.pop(0)
            if pathLeft:
                self.LFile = pathLeft + self.metadata.imageExtension
                self.gvLeft.setImageFromFile(self.LFile)
                self.gvLeft.fillExtent()

                #  get the UTC corrected time string
                timeString = (self.metadata.imageData[self.leftCamera][number][1].strftime('%Y-%m-%d %H:%M:%S') +
                        '.%03d' % (self.metadata.imageData[self.leftCamera][number][1].microsecond / 1000.))

                if (self.leftDateTimeLabel != None):
                    self.gvLeft.removeHudItem(self.leftDateTimeLabel)
                    self.gvLeft.removeHudItem(self.leftFrameLabel)
                    self.gvLeft.removeHudItem(self.leftEnhanceLabel)

                self.leftDateTimeLabel = self.gvLeft.addHudText(QPointF(0.98,0.99),
                        timeString, color=[0,250,0], alpha=150, halign='right',
                        valign='bottom')

                self.leftFrameLabel = self.gvLeft.addHudText(QPointF(0.02,0.99),
                        'Frame: ' + str(number), color=[0,250,0], alpha=150,
                        halign='left', valign='bottom')

                if (self.gvLeft.image.enhancementsEnabled):
                    self.leftEnhanceLabel = self.gvLeft.addHudText(QPointF(0.02,0.001),
                            'Enhancements: On', color=[0,250,0], alpha=150,
                            halign='left', valign='top')
                else:
                    self.leftEnhanceLabel = self.gvLeft.addHudText(QPointF(0.02,0.001),
                            'Enhancements: Off', color=[0,250,0], alpha=150,
                            halign='left', valign='top')
            else:
                self.gvLeft.clearViewer()

        if (len(self.rightImageQueue) > 0):
            #  get the next right image number and path
            number, pathRight = self.rightImageQueue.pop(0)
            if pathRight:
                self.RFile=pathRight + self.metadata.imageExtension
                self.gvRight.setImageFromFile(self.RFile)
                self.gvRight.fillExtent()

                #  get the UTC corrected time string
                timeString = (self.metadata.imageData[self.rightCamera][number][1].strftime('%Y-%m-%d %H:%M:%S') +
                        '.%03d' % (self.metadata.imageData[self.rightCamera][number][1].microsecond / 1000.))

                if (self.rightDateTimeLabel != None):
                    self.gvRight.removeHudItem(self.rightDateTimeLabel)
                    self.gvRight.removeHudItem(self.rightFrameLabel)
                    self.gvRight.removeHudItem(self.rightEnhanceLabel)

                self.rightDateTimeLabel = self.gvRight.addHudText(QPointF(0.98,0.99),
                        timeString, color=[0,250,0], alpha=150, halign='right',
                        valign='bottom')

                self.rightFrameLabel = self.gvRight.addHudText(QPointF(0.02,0.99),
                        'Frame: ' + str(number), color=[0,250,0], alpha=150,
                        halign='left', valign='bottom')

                if (self.gvRight.image.enhancementsEnabled):
                    self.rightEnhanceLabel = self.gvRight.addHudText(QPointF(0.02,0.001),
                            'Enhancements: On', color=[0,250,0], alpha=150,
                            halign='left',valign='top')
                else:
                    self.rightEnhanceLabel = self.gvRight.addHudText(QPointF(0.02,0.001),
                            'Enhancements: Off', color=[0,250,0], alpha=150,
                            halign='left', valign='top')
            else:
                self.gvRight.clearViewer()


        #  update the attitude/depth info
        try:
            attitudeString = self.metadata.sensorData['CTControl']['$OHPR'][number]
            stringParts = attitudeString.split(',')
            self.yaw.setText(self.convertFloatToString(stringParts[1]))
            self.pitch.setText(self.convertFloatToString(stringParts[2]))
            self.roll.setText(self.convertFloatToString(stringParts[3]))
            self.depth.setText(self.convertFloatToString(stringParts[5]))
        except:
            #  there probably isn't any sensor data available...
            pass


    def convertFloatToString(self, val, format='%.1f', badVal='--.-'):
        """
        convertFloatToString is a simple internal function to convert unformatted
        float values which are represented as strings to a formatted float value
        that is represented as a string. You can optionally provide the format string.
        If a value is not convertable to a float, the badVal string will be returned.
        """

        try:
            val = format % (float(val))
        except:
            val = badVal

        return val


    def changeImage(self):
        '''
        This method is called whenever the image number changes. Images are put into a
        queue to be loaded by a timer event. We do this so we can easily discard images
        when the user drags the slider so the GUI doesn't get bogged down sequentially
        loading all of those images.
        '''

        #  get the current image index
        imageIndex = self.imageSlider.value()

        #  and use the index to get the image number
        number = self.metadata.imageNumbers[imageIndex]

        #  ensure that the number has changed
        if (number == self.lastNumberLoaded):
            return

        #  this is a new image
        self.lastNumberLoaded = number

        #  update the marks GUI elements. We can do that here since
        #  there is little cost. No need to queue this.
        if number in self.metadata.marks:
            self.marksDescription.setText(self.metadata.marks[number])
            self.pbDeleteMark.setEnabled(True)
        else:
            self.marksDescription.setText('')
            self.pbDeleteMark.setEnabled(False)

        #  get the left image name
        try:
            imageName = self.metadata.imageData[self.leftCamera][number][2]
            imagePath = str(self.dataDir + os.path.sep + "images" + os.path.sep +
                    self.leftCamera + os.path.sep + imageName)
            leftImage = os.path.normpath(imagePath)
        except:
            leftImage = None

        #  check the length of our left image queue and trim if needed
        nQueued = len(self.leftImageQueue)
        if nQueued > self.maxQueuedImages:
            self.leftImageQueue.pop(0)
        self.leftImageQueue.append([number, leftImage])

        #  get the right image name
        try:
            imageName = self.metadata.imageData[self.rightCamera][number][2]
            imagePath = str(self.dataDir + os.path.sep + "images" + os.path.sep +
                    self.rightCamera + os.path.sep + imageName)
            rightImage = os.path.normpath(imagePath)
        except:
            rightImage = None

        #  check the length of our queue and trim if needed
        nQueued = len(self.rightImageQueue)
        if nQueued > self.maxQueuedImages:
            self.rightImageQueue.pop(0)
        self.rightImageQueue.append([number, rightImage])


    def exportImages(self):
        """
        exportImages exports the currently displayed images to a folder. They will be
        exported with corrections applied. The name will be the same as the source
        file name.
        """

        #  get the export directory name
        dirDlg = QFileDialog(self)
        dirName = dirDlg.getExistingDirectory(self, 'Select Export Location', self.copyDir,
                QFileDialog.Option.ShowDirsOnly)
        if (dirName):

            dirName = str(dirName)
            #  build the export file name and export the left image
            p, f = os.path.split(str(self.LFile))
            filename = dirName + os.path.sep + f
            filename = os.path.normpath(filename)
            self.gvLeft.saveImage(filename)

            #  build the export file name and export the right image
            p, f = os.path.split(str(self.RFile))
            filename = dirName + os.path.sep + f
            filename = os.path.normpath(filename)
            self.gvRight.saveImage(filename)



    def speedSet(self):
        self.playTimer.setInterval(int(1./self.playSpeedDial.value()*1000))


    def play(self):
        if self.playBtn.isChecked():
            self.playBtn.setStyleSheet(self.green)
            self.playTimer.setInterval(int(1./self.playSpeedDial.value()*1000))
            self.playTimer.start()
        else:
            self.playBtn.setStyleSheet(self.gray)
            self.playTimer.stop()


    def exportData(self):

        #  get the directory to export to
        dirDlg = QFileDialog(self)
        dirName = dirDlg.getExistingDirectory(self, 'Select Export Directory',
                self.copyDir, QFileDialog.Option.ShowDirsOnly)
        if (dirName != None):

            dataDir = os.path.normpath(self.dataDir)
            exportBasename = dirName + os.path.sep + dataDir.split(os.path.sep)[-1] + '_'
            exportBasename = os.path.normpath(exportBasename)

            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.statusBar.showMessage('Exporting metadata...')

            try:
                #  disable the QImageViewers while exporting
                self.gvLeft.setEnabled(False)
                self.gvRight.setEnabled(False)
                #  export
                self.metadata.exportMetadataToCSV(exportBasename)
                #  enable the QImageViewers
                self.gvLeft.setEnabled(True)
                self.gvRight.setEnabled(True)
                #  reset the GUI
                self.statusBar.clearMessage()
                QApplication.restoreOverrideCursor()
                #  report success
                QMessageBox.information(self, "Export", "Metadata export files created.")
            except Exception as e:
                #  there was a problem - enable the QImageViewers
                self.gvLeft.setEnabled(True)
                self.gvRight.setEnabled(True)
                #  reset the GUI
                self.statusBar.clearMessage()
                QApplication.restoreOverrideCursor()

                print(e)
                QMessageBox.critical(self, "Export Failure", "Error exporting deployment metadata.")


    def moveSlider(self):
        self.imageSlider.setValue(self.imageSlider.value()+1)


    def checkWindowLocation(self, position, size, padding=[5, 25]):
        '''
        checkWindowLocation accepts a window position (QPoint) and size (QSize)
        and returns a potentially new position and size if the window is currently
        positioned off the screen.

        This function uses QScreen.availableVirtualGeometry() which returns the full
        available desktop space *not* including taskbar. For all single and "typical"
        multi-monitor setups this should work reasonably well. But for multi-monitor
        setups where the monitors may be different resolutions, have different
        orientations or different scaling factors, the app may still fall partially
        or totally offscreen. A more thorough check gets complicated, so hopefully
        those cases are very rare.

        If the user is holding the <shift> key while this method is run, the
        application will be forced to the primary monitor.
        '''

        #  create a QRect that represents the app window
        appRect = QRect(position, size)

        #  check for the shift key which we use to force a move to the primary screem
        resetPosition = QGuiApplication.queryKeyboardModifiers() == Qt.KeyboardModifier.ShiftModifier
        if resetPosition:
            position = QPoint(padding[0], padding[0])

        #  get a reference to the primary system screen - If the app is off the screen, we
        #  will restore it to the primary screen
        primaryScreen = QGuiApplication.primaryScreen()

        #  assume the new and old positions are the same
        newPosition = position
        newSize = size

        #  Get the desktop geometry. We'll use availableVirtualGeometry to get the full
        #  desktop rect but note that if the monitors are different resolutions or have
        #  different scaling, some parts of this rect can still be offscreen.
        screenGeometry = primaryScreen.availableVirtualGeometry()

        #  if the app is partially or totally off screen or we're force resetting
        if resetPosition or not screenGeometry.contains(appRect):

            #  check if the upper left corner of the window is off the left side of the screen
            if position.x() < screenGeometry.x():
                newPosition.setX(screenGeometry.x() + padding[0])
            #  check if the upper right is off the right side of the screen
            if position.x() + size.width() >= screenGeometry.width():
                p = screenGeometry.width() - size.width() - padding[0]
                if p < padding[0]:
                    p = padding[0]
                newPosition.setX(p)
            #  check if the top of the window is off the top/bottom of the screen
            if position.y() < screenGeometry.y():
                newPosition.setY(screenGeometry.y() + padding[0])
            if position.y() + size.height() >= screenGeometry.height():
                p = screenGeometry.height() - size.height() - padding[1]
                if p < padding[0]:
                    p = padding[0]
                newPosition.setY(p)

            #  now make sure the lower right (resize handle) is on the screen
            if (newPosition.x() + newSize.width()) > screenGeometry.width():
                newSize.setWidth(screenGeometry.width() - newPosition.x() - padding[0])
            if (newPosition.y() + newSize.height()) > screenGeometry.height():
                newSize.setHeight(screenGeometry.height() - newPosition.y() - padding[1])

        return [newPosition, newSize]

if __name__ == "__main__":

    app = QApplication(sys.argv)
    form = CamtrawlBrowser()
    form.show()
    app.exec()

