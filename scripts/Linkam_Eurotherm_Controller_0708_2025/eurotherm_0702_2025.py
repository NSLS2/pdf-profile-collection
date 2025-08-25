# Cryostat T-dependent XRD and PDF measurements
# Created: 11/09/2020 (MA)
#updated on 8/25/2025 CHL, GK

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
#A=list(range(30,700,20)) 
# A=list(range(500, 45, -5)) 
A=[170, 180, 190, 200]
B = [300, 400, 500]
#A = list(range(30, 900, 20))
#A = [30, 35, 30]
#C=list(range(955,500,-5))
#D=list(range(500,50,-10))  
T_threshold = 1	     	     # T-setpoint +-threshold
Settle_time = 300	             # Settle time (sec) after Linkam reach the setpoint	Temperature

# Tlist= A+B
Tlist = B

smpi = 0 #59             # sample index
spi = 0  #4 #5                 # scan plan index

Option_1 = 1            # 0 for both XRD & PDF, 1 for only PDF, and 2 for only XRD measuremnts
num_repaet_PDF = 5
num_repaet_XRD = 1
rest_repeat = 2 #60      # Rest time during each repeat to clear the detector

Det_PDF = 4086 #3070               # PDF detector position
Det_XRD = 4086 #3770               # XRD detector position

D1 = Det_PDF
D2 = Det_XRD

det_exp_PDF = 0.2	# for option 0
det_exp_XRD = 0.2	# for option 0

glbl['frame_acq_time'] = 0.1	#Deatector frame acquasition time
glbl['dk_window'] = 0.1         # dark current acquasition window
st2 = 5 #30                 	# sleep time after first PDF and XRD measuement at option 0(zero)

thermal_device = eurotherm3504  #linkam_T96

plt.figure()
#======================================= Definition of Measuremet =======================================
# Do not change anyhing below.  

Time, Tset, T1, T2, Temperature, DetZ = [],[],[],[],[],[]
Tseries = list(bt.samples.keys())[smpi] 
# data_dir = "/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/tiff_base/" + str(Tseries) + "/dark_sub/"
# data_dir_2 = "/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/tiff_base/" + str(Tseries) + "/integration/"
# config_dir = "/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/"

# os.makedirs(data_dir, exist_ok=True)
# os.makedirs(data_dir_2, exist_ok=True)


def tqdm_sleep(rest_time, message='Sleep'):
    from tqdm import tqdm
    for j in tqdm(range(0,100), desc=message):
        time.sleep(rest_time/100)


def measurement(num_repeat, rest_time=1, frame_time=0.1, Settle_time=10):
	DetZ.append(round(Det_1_Z.position))
	
	try:
		tset = thermal_device.setpoint.get()  #for linkham get target temperature
	except AttributeError:
		tset = thermal_device.setpoint        #for eurotherm 

	tqdm_sleep(Settle_time, message='Wait for thermal equilibrium')

	Tset.append(tset)

	try:
		t1 = thermal_device.readback.get()
	except AttributeError:
		t1 = thermal_device.get()

	for i in range(num_repeat):
		xrun(smpi,spi,useful_info = measurement_data())
		glbl['frame_acq_time'] = 0.1
		tqdm_sleep(rest_time, message='Clear detector')
		glbl['frame_acq_time'] = frame_time


	try:
		t2 = thermal_device.readback.get()
	except AttributeError:
		t2 = thermal_device.get()
	
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
	tqdm_sleep(1)
	Data_out= c_[Time, Tset, T1, T2, Temperature, DetZ] # arrange data to column format
	# data_fn = os.path.join(data_dir, "measurement_data.DAT")
	# np.savetxt(data_fn, Data_out) # save data

#=================================== Measurement Logic  ====================================

if Option_1 == 0:   # PDF and XRD
	for i in range(len(Tlist)):
		glbl['frame_acq_time'] = det_exp_PDF
		# RE(mv(thermal_device,Tlist[i]))
		print(f'\nmove {thermal_device.name} to {Tlist[i]}\n')
		thermal_device.move(Tlist[i])    
		#Det_1_Z.move(D1)
		move_PDF()
		measurement(num_repaet_PDF, rest_time=rest_repeat, frame_time=det_exp_PDF, Settle_time=Settle_time)
		glbl['frame_acq_time'] = 0.1
		tqdm_sleep(st2, message='Sleep after PDF')
		glbl['frame_acq_time'] = det_exp_XRD
		#Det_1_Z.move(D2)
		move_XRD()
		measurement(num_repaet_XRD, rest_time=rest_repeat, frame_time=det_exp_XRD, Settle_time=Settle_time)
		tqdm_sleep(st2, message='Sleep after XRD')
    
if Option_1 == 1:   #PDF 
	#Det_1_Z.move(D1)
	glbl['frame_acq_time'] = det_exp_PDF
	move_PDF()
	for i in range(len(Tlist)):
		print(f'\nmove {thermal_device.name} to {Tlist[i]}\n')
		thermal_device.move(Tlist[i])
		measurement(num_repaet_PDF, rest_time=rest_repeat, frame_time=det_exp_PDF, Settle_time=Settle_time)
		tqdm_sleep(st2, message='Sleep after PDF')

if Option_1 == 2:   #XRD
	#Det_1_Z.move(D2)
	glbl['frame_acq_time'] = det_exp_XRD
	move_XRD()
	for i in range(len(Tlist)):
		print(f'\nmove {thermal_device.name} to {Tlist[i]}\n')
		thermal_device.move(Tlist[i])
		measurement(num_repaet_XRD, rest_time=rest_repeat, frame_time=det_exp_XRD, Settle_time=Settle_time)
		tqdm_sleep(st2, message='Sleep after XRD')


Data_out= c_[Time, Tset, T1, T2, Temperature, DetZ]
#------------------------------------------------------------------

plot(Time, Temperature,'r-') # plot a line at the end - time vs T
xlabel("Time")
ylabel("Temperature")
time.sleep(10)


#===Create a duplicate set of files and append Time, detector/sample position and temperature in their names====
# os.chdir(data_dir)
# A = []

# for file in os.listdir(data_dir):
#     if file.endswith("tiff"):
#         A.append(file)
# A.sort(key=lambda x: os.path.getmtime(x))

# l=0
# L=100

# try:
# 	for file in A:
# 		arr = imread(file)
# 		imsave((data_dir + str(Tseries) + "_" + str(L) +"_T_"+ str(Data_out[l][4]) + "K_DetZ_" + str(Data_out[l][5])+ "_mm" + ".tiff"), arr)
# 		l = l + 1
# 		L = L + 1
# 		print (l)
            
# except (IndexError, KeyError):
#       pass

# #------------------ Move XRD and PDF data into different folders---------------------
# directory_1 = "PDF"
# directory_2 = "XRD"
# directory_3 = "original"

# path_1 = os.path.join(data_dir, directory_1)
# path_2 = os.path.join(data_dir, directory_2)
# path_3 = os.path.join(data_dir, directory_3)
# os.mkdir(path_1)
# os.mkdir(path_2)
# os.mkdir(path_3)

# for file in os.listdir(data_dir): 
#     if file.endswith(str(float(D1))+ "_mm.tiff"): 
#         shutil.move(file, data_dir + "./PDF")
# for file in os.listdir(data_dir): 
#     if file.endswith(str(float(D2)) + "_mm.tiff"): 
#         shutil.move(file, data_dir + "./XRD")
# time.sleep(4)
# for file in os.listdir(data_dir): 
#     if file.endswith(".tiff"): 
#         shutil.move(file, data_dir + "./original")  

#--------------------

'''
#---------------------------------HAB T setpoint threshold--------------------------------------------
def HAB_Tset(t, threshold, settle_time):
	caput("XF:28ID1-ES:1{Env:05}LOOP1:SP", t)
	T_now = hotairblower.get()

	while T_now not in range(t-threshold, t+2*threshold):
		T_now = hotairblower.get()
		time.sleep(0.5)
	time.sleep(settle_time)
'''



