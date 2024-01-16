'''

This script is used to compare and calibrate the Camtrawl pressure sensor
to data obtained by an SBE attached to the Camtrawl frame. It first plots
the existing Camtrawl depths with the SBE depths, then backs out the Camtrawl
calibration and computes a new fit for the raw data and applies those
parameters to the raw data and plots the new calibrated depths with the
SBE data. It also presents the new slope and intercept (aka offset) values
in the upper left of this figure. These new cal values should then be
entered into the Zoidberg application and programmed in Camtrawl.

There are a number of variables you must set at the top of the runCal
method below before running this script. This script also requires
that the SBE data be downloaded into clamsbase. Database credentials
must be entered in at the bottom of the script.

'''
import math
import datetime
import  CamtrawlMetadata
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as interp
import dbConnection
from PyQt6 import QtCore


def asc_file_to_depth(filename, latitude):

    def pressureToDepth(p, lat):
        '''
        calculates depth based on latitude and pressure. From:
        Unesco 1983. Algorithms for computation of fundamental properties of
        seawater, 1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.
        '''

        deg2rad = math.pi / 180.0

        # Eqn 25, p26.  UNESCO 1983.
        c = [9.72659, -2.2512e-5, 2.279e-10, -1.82e-15]
        gam_dash = 2.184e-6

        lat = abs(lat)
        X = math.sin(lat * deg2rad)
        X = X * X

        bot_line = (9.780318 * (1.0 + (5.2788e-3 + 2.36e-5 * X) * X) + gam_dash * 0.5 * p)
        top_line = (((c[3] * p + c[2]) * p + c[1]) * p + c[0]) * p

        return top_line / bot_line


    sbe_depth = []
    sbe_time = []

    f = open(filename, 'r')

    #  read the lines in the header and discard
    in_header = True
    while in_header:
        line = f.readline().rstrip('\n')
        if line is None:
            #  file must have ended in the header?
            break
        if line == '*END*':
            #  almost at the end of the header, read the next 3 lines
            f.readline()
            f.readline()
            f.readline()
            in_header = False
            break

    #  now read the data lines
    line = f.readline().rstrip('\n')
    while line:
        temp, pressure, sample_date, sample_time = line.split(',')

        timestr = sample_date.strip() + sample_time

        try:
            t = datetime.datetime.strptime(timestr, '%d %b %Y %H:%M:%S')
            d = pressureToDepth(float(pressure), float(latitude))

            sbe_time.append(t)
            sbe_depth.append(d)
        except:
            pass

        line = f.readline().rstrip('\n')

    return sbe_depth, sbe_time


class calibrate_depth_sensor(QtCore.QObject):

    def __init__(self, odbcSource, user, password):

        super(calibrate_depth_sensor, self).__init__()

        #  create an instance of our dbConnection
        self.db = dbConnection.dbConnection(odbcSource, user, password)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.runCal)
        timer.setSingleShot(True)
        timer.start(1)


    def runCal(self):

        #  set to True to extract SBE depth values from clamsbase. If you downloaded
        #  data from the SBE using CLAMS_SBE_Downloader then set this to true. If
        #  you downloaded SBE data using SeaTerm to create an .asc file set this to
        #  false
        useDatabase = True

        #  define the path to the CamTrawl metadata database file
        camtrawlDb = 'X:/DY2400/Camtrawl/Haul_001/D20240114-T214626'
        #camtrawlDb = 'C:/Users/rick.towler/Desktop/Coral Dropcam Depth Calibration'
        #camtrawlDb = 'C:/Users/rick.towler/Work/CoralDepthCal_23/D20230703-T022422'

        #  define the path to the SBE data file (.asc) file
        #sbeASCFile = 'C:/Users/rick.towler/Desktop/Coral Dropcam Depth Calibration/calibration station.asc'
        sbeASCFile = 'C:/Users/rick.towler/Work/CoralDepthCal_23/testdrop2.asc'


        #sbe_latitude = 59.6
        sbe_latitude = 47.7

        #  specify the smoothing window for the CT depth data (needs to be odd)
        smoothWindow = 15

        #  specify the existing slope and intercept of the camtrawl system
        #  obtained from the zoidberg app on camtrawl. These are used to back
        #  out the existing calibration to obtain raw sensor values.
        ex_slope = 0.05703
        ex_intercept = -159.5663

        #  Specify the time offset of CamTrawl when compared to the SBE data.
        #  If things are working this shouldn't be required and the offset
        #  should be set to 0
        CamTrawlTimeOffset = 0# -60*60*7


        #  These settings are only relevant when useDatabase is set to True

        #  define the ship, survey, and event id we're going to pull the SBE data from
        ship = '999'
        survey = '201499'
        event_id = '20'

        #  define the SBE device ID of the SBE connected to CamTrawl
        #  THIS IS THE DEVICE ID, NOT THE SERIAL NUMBER
        device_id = '46'

        # ======================================================================

        #  set a reference point to serialize time to
        epoch = datetime.datetime(1970,1,1)

        #  create the time delta to use to align Camtrawl and SBE data
        CamTrawlTimeDelta =  datetime.timedelta(seconds=CamTrawlTimeOffset)

        #  query the SBE data
        sbe_depth = []
        sbe_time = []

        if useDatabase:
            #  open the connection - dbOpen will raise an error if it can't connect
            try:
                self.db.dbOpen()
            except Exception as err:
                print("ooops, we couldn't open up the database")
                print(err)
                QtCore.QCoreApplication.instance().quit()

            #  and query the data from clamsbase
            sql = ("SELECT TO_CHAR(time_stamp), measurement_value FROM event_stream_data WHERE ship=" + ship +
                    " AND survey=" + survey + " AND event_id=" + event_id +
                    " AND device_id=" + device_id + " AND measurement_type='SBEDepth' " +
                    "ORDER BY time_stamp ASC")
            print(sql)
            query = self.db.dbQuery(sql)
            for timestamp_str, depth in query:
                sbe_depth.append(float(depth))
                timestamp = datetime.datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S.%f')
                sbe_time.append(timestamp)

        else:

            #  we're not using the database so we get depth from an SBE .asc file
            #  created when downloading from Seaterm.
            sbe_depth, sbe_time = asc_file_to_depth(sbeASCFile, sbe_latitude)

        #  get the start end end SBE times
        sbeStartTime = sbe_time[0]
        sbeEndTime = sbe_time[-1]

        #  convert the SBE time to serial time
        for i in range(len(sbe_time)):
           sbe_time[i] = (sbe_time[i] - epoch).total_seconds()

        #  open the CamTrawl metadata database file
        ctData = CamtrawlMetadata.CamTrawlMetadata()
        ctData.open(camtrawlDb)

        #  call the query method to read and extract our metadata
        #  we specify the start and end time to constrain to the SBE time
        ctData.query(startTime=sbeStartTime, endTime=sbeEndTime)

        #  grab the camera with the most images
        nImages = -1
        cameras = list(ctData.cameras.keys())
        for cam in ctData.cameras.keys():
            n = len(ctData.imageData[cam])
            if (n > nImages):
                nImages = n

        #  get the CamTrawl depth and time
        ct_depth = []
        ct_time = []
        ct_datetime = []
        for key in ctData.sensorData['CTControl']['$OHPR']:
            data = ctData.sensorData['CTControl']['$OHPR'][key]
            data = data.split(',')
            ct_depth.append(float(data[5]))
            #  get the image times - if we drop an image, the "key" will not exist so
            #  we try the first camera and if we fail we try the second camera.
            try:
                #  get the UTC time of this image (it's the 2nd time - index 1)
                ct_datetime.append(ctData.imageData[cameras[0]][key][1] - CamTrawlTimeDelta)
                #  for interpolation we need a serial time
                ct_time.append((ctData.imageData[cameras[0]][key][1] - epoch).total_seconds() - CamTrawlTimeOffset)
            except:
                #  get the UTC time of this image (it's the 2nd time - index 1)
                ct_datetime.append(ctData.imageData[cameras[1]][key][1] - CamTrawlTimeDelta)
                #  for interpolation we need a serial time
                ct_time.append((ctData.imageData[cameras[1]][key][1] - epoch).total_seconds() - CamTrawlTimeOffset)

        #  convert our lists to numpy arrays
        ct_depth = np.asarray(ct_depth)
        ct_time = np.asarray(ct_time)
        sbe_depth = np.asarray(sbe_depth)
        sbe_time = np.asarray(sbe_time)

        #  smooth the CamTrawl depth path
        hanning_window = np.hanning(smoothWindow)
        ct_depth = np.convolve(hanning_window/hanning_window.sum(), ct_depth, mode='same')

        #  trim the smoothed path to remove smoothing tails
        ct_depth = ct_depth[smoothWindow:-smoothWindow]
        ct_time = ct_time[smoothWindow:-smoothWindow]
        ct_datetime = ct_datetime[smoothWindow:-smoothWindow]

        #  interpolate the SBE data so it is the same x values as camtrawl
        f = interp.interp1d(sbe_time, sbe_depth)
        sbe_depth_interp = f(ct_time)


        #  ------------   Compare the existing data   ------------
        #  create a figure
        fig = plt.figure(figsize=(12,7))

        #  plot the SBE data
        plt.plot(ct_datetime, sbe_depth_interp, color=(0,1,0,1), label='SBE')

        #  plot the CamTrawl data
        plt.plot(ct_datetime, ct_depth,  color=(1,0,0,1), label='Camtrawl')

        #  dress up the figure
        plt.gca().invert_yaxis()
        plt.ylabel('depth (m)')
        plt.xlabel('Time')
        title = 'unmodified pressure sensor comparison'
        fig.suptitle(title, fontsize=18)
        plt.legend()

        #  and show
        plt.show(block=True)


        #  ------------   Compute the calibration params   ------------

        #  convert ct depth back to raw values
        ct_depth = ct_depth - ex_intercept
        ct_depth = ct_depth / ex_slope

        #  calculate the new calibration parameters
        a, b = np.polyfit(ct_depth, sbe_depth_interp, 1)

        #  apply them to the CamTrawl data
        ct_depth = (ct_depth * a) + b

        #  create a figure
        fig = plt.figure(figsize=(12,7))

        #  plot the SBE data
        plt.plot(ct_datetime, sbe_depth_interp, color=(0,1,0,1), label='SBE')

        #  plot the CamTrawl data
        plt.plot(ct_datetime, ct_depth,  color=(1,0,0,1), label='Camtrawl')

        #  dress up the figure
        plt.gca().invert_yaxis()
        fig.text(0.01, 0.955, ('slope: %10.5f' % a))
        fig.text(0.01, 0.93, ('offset: %9.3f' % b))
        plt.ylabel('depth (m)')
        plt.xlabel('Time')
        title = 'calibrated pressure sensor comparison'
        fig.suptitle(title, fontsize=18)
        plt.legend()

        print(a)
        print(b)

        #  and show
        plt.show(block=True)

        #  close the connection
        ctData.close()
        self.db.dbClose()

        #  quit
        QtCore.QCoreApplication.instance().quit()


if __name__ == "__main__":
    import sys
    app = QtCore.QCoreApplication(sys.argv)
    form = calibrate_depth_sensor('afsc-64', 'clamsbase2', 'pollock')
    sys.exit(app.exec())



