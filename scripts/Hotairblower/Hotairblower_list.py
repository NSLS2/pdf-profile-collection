# Cryostat T-dependent XRD and PDF measurements
# Created: 11/09/2020 (MA)

import time
import pylab
from pylab import *
import numpy as np
import os
from tifffile import imread, imsave
import matplotlib.pyplot as plt 
import shutil 
 
#======================================== Definition of variables =======================================
# Users plese change variables as necessay

#A=list(range(125,300,25))
A=list(range(40,500,5)) 
A=list(range(500, 45, -5)) 
#C=list(range(955,500,-5))
#D=list(range(500,50,-10))  
T_threshold = 1	     	     # T-setpoint +-threshold
Settle_time = 2		     # Settle time after HAB reach the setpoint	Temperature

Tlist= A+B

smpi = 20                # sample index
spi = 4                 # scan plan index

Option_1 = 0            # 0 for both XRD & PDF, 1 for only PDF, and 2 for only XRD measuremnts

D1 = 3675               # PDF detector position
D2 = 4475               # XRD detector position

glbl['frame_acq_time'] = 0.5   # Deatector frame acquasition time
glbl['dk_window'] = 0.1         # dark current acquasition window
st2 = 0                 	# sleep timebefore each measuement

plt.figure()
#======================================= Definition of Measuremet =======================================
# Do not change anyhing below.  

Time, Tset, T1, T2, Temperature, DetZ = [],[],[],[],[],[]
Tseries = list(bt.samples.keys())[smpi] 
data_dir = "/nsls2/xf28id1/xpdacq_data/user_data/tiff_base/" + str(Tseries) + "/dark_sub/"
data_dir_2 = "/nsls2/data/pdf/legacy/processed/xpdacq_data/user_data/tiff_base/" + str(Tseries) + "/integration/"
config_dir = "/nsls2/data/pdf/legacy/processed/xpdacq_data/user_data/config_base/"

def move_PDF():
    os.remove(config_dir + "xpdAcq_calib_info.poni")
    shutil.copy(config_dir + "/PDF/" + "xpdAcq_calib_info.poni" , config_dir)

def move_XRD():
    os.remove(config_dir + "xpdAcq_calib_info.poni")
    shutil.copy(config_dir + "/XRD/" + "xpdAcq_calib_info.poni" , config_dir)

def measurement():
    DetZ.append(round(Det_1_Z.position))
    tset = caget("XF:28ID1-ES:1{Env:05}LOOP1:SP")
    Tset.append(tset)
    t1 = hotairblower.get()
    xrun(smpi,spi)
    t2 = hotairblower.get()
    T = (t1 + t2)/2
    T1.append(t1)
    T2.append(t2)
    time1 = round(time.time())
    Time.append(time1)
    Temperature.append(round (T, 1))

#   sack_message(str(round(T,1)) + " K " + " mm Det1_Z " + str(round(Det_1_Z.position)) + " mm measurement completed")
    
    plt.plot(time1,T,'bo')
    plt.ion()   # produce an interactive time vs temperature plot
    plt.pause(0.05)
    time.sleep(1)
    Data_out= c_[Time, Tset, T1, T2, Temperature, DetZ] # arrange data to column format
    np.savetxt(data_dir + str(Tseries) + "measurement_data.DAT", Data_out) # save data

#=================================== Measurement Logic  ====================================

if Option_1 == 0:   # PDF and XRD
	for i in range(len(Tlist)):
		HAB_Tset(Tlist[i], T_threshold, Settle_time)
		Det_1_Z.move(D1)
        move_PDF()
		measurement()
		Det_1_Z.move(D2)
        move_XRD()
		measurement()
    
if Option_1 == 1:   #PDF 
	Det_1_Z.move(D1)
    move_PDF()
	for i in range(len(Tlist)):
		HAB_Tset(Tlist[i], T_threshold, Settle_time)
		measurement()

if Option_1 == 2:   #XRD
	Det_1_Z.move(D2)
    move_XRD()
	for i in range(len(Tlist)):
		HAB_Tset(Tlist[i], T_threshold, Settle_time)
		measurement()


Data_out= c_[Time, Tset, T1, T2, Temperature, DetZ]
#------------------------------------------------------------------

plot(Time, Temperature,'r-') # plot a line at the end - time vs T
xlabel("Time")
ylabel("Temperature")
time.sleep(10)


#===Create a duplicate set of files and append Time, detector/sample position and temperature in their names====
os.chdir(data_dir)
A = []

for file in os.listdir(data_dir):
    if file.endswith("tiff"):
        A.append(file)
A.sort(key=lambda x: os.path.getmtime(x))

l=0
L=100

for file in A:
    arr = imread(file)
    imsave((data_dir + str(Tseries) + "_" + str(L) +"_T_"+ str(Data_out[l][4]) + "K_DetZ_" + str(Data_out[l][5])+ "_mm" + ".tiff"), arr)
    l = l + 1
    L = L + 1
    print (l)

#------------------ Move XRD and PDF data into different folders---------------------
directory_1 = "PDF"
directory_2 = "XRD"
directory_3 = "original"

path_1 = os.path.join(data_dir, directory_1)
path_2 = os.path.join(data_dir, directory_2)
path_3 = os.path.join(data_dir, directory_3)
os.mkdir(path_1)
os.mkdir(path_2)
os.mkdir(path_3)

for file in os.listdir(data_dir): 
    if file.endswith(str(float(D1))+ "_mm.tiff"): 
        shutil.move(file, data_dir + "./PDF")
for file in os.listdir(data_dir): 
    if file.endswith(str(float(D2)) + "_mm.tiff"): 
        shutil.move(file, data_dir + "./XRD")
time.sleep(4)
for file in os.listdir(data_dir): 
    if file.endswith(".tiff"): 
        shutil.move(file, data_dir + "./original")  

#--------------------

