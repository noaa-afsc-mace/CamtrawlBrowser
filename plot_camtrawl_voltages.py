
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import CamtrawlMetadata


metadata_file = 'C:/Users/rick.towler/Work/AFSCGit/CamTrawl/DY2304 plot_volts/2207-haul 68'

idxs = [0, 500]
idxc = [0, 100]


def toFloat(val):
    try:
        f = float(val)
    except:
        f = np.nan

    return f



print('Reading metadata...')
metadata = CamtrawlMetadata.CamTrawlMetadata()
metadata.open(metadata_file)
metadata.query()


#  extract the system voltage and IMU temp
batteryVoltage = []
imuTemp = []
batteryTime = []
for i in range(0, len(metadata.asyncData['CTControl']['$CTSV']['utc_time'])):
    #  split the sensor string
    parts = metadata.asyncData['CTControl']['$CTSV']['data'][i].split(',')
    #  get the time
    batteryTime.append(metadata.asyncData['CTControl']['$CTSV']['utc_time'][i])
    #  convert temp and voltage to a float and store
    batteryVoltage.append(toFloat(parts[2]))
    imuTemp.append(toFloat(parts[3]))

#  get the camera voltage and temp
cameraVoltage = {}
cameraTemp = {}
cameraTime = {}
#  generate dicts keyed by camera to hold temp, voltage, and time
cameras = list(metadata.cameras.keys())
for c in cameras:
    cameraVoltage[c] = []
    cameraTemp[c] = []
    cameraTime[c] = []
#  and populate these lists
for i in range(0, len(metadata.asyncData['Camera']['$CTCS']['utc_time'])):
    #  split the sensor string
    parts = metadata.asyncData['Camera']['$CTCS']['data'][i].split(',')
    #  get the time
    cameraTime[parts[1]].append(metadata.asyncData['Camera']['$CTCS']['utc_time'][i])
    #  convert temp and voltage to a float and store
    cameraVoltage[parts[1]].append(toFloat(parts[2][1:-1]))
    cameraTemp[parts[1]].append(toFloat(parts[4]))

mpl.style.use('seaborn')
fig, axes = plt.subplots(nrows=2)

#  plot the voltages
for i in range(0,len(cameras)):
    camera = cameras[i]
    color = 'C' + str(i)
    
    axes[0].plot(cameraTime[camera][idxc[0]:idxc[1]],cameraVoltage[camera][idxc[0]:idxc[1]],color, label=camera)
axes[0].plot(batteryTime[idxs[0]:idxs[1]],batteryVoltage[idxs[0]:idxs[1]],'C5', label='System')
axes[0].set(xlabel='Time', ylabel='Voltage (V)',
    title='System Voltages')
axes[0].legend()

#  plot the temps
for i in range(len(cameras)):
    camera = cameras[i]
    color = 'C' + str(i)
    axes[1].plot(cameraTime[camera][idxc[0]:idxc[1]],cameraTemp[camera][idxc[0]:idxc[1]],color, label=camera)
axes[1].plot(batteryTime[idxs[0]:idxs[1]],imuTemp[idxs[0]:idxs[1]],'C5', label='System')
axes[1].set(xlabel='Time', ylabel='Temperature (C)',
    title='System Temperatures')
axes[1].legend()

#  fancy up the x labels
fig.autofmt_xdate()

#  add a figure title
#fig.suptitle('Camera Deployment ' + str(self.deployment.text()), fontsize=16)

#  show the plot
plt.show()
