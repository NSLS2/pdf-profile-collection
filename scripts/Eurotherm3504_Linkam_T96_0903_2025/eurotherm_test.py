from epics import PV
from epics import caget, caput
import datetime
import numpy as np
import pylab
from pylab import *
import os
from tifffile import imsave,  imread
import sys

glbl['dk_window']=0.1
time.sleep(2)
glbl['frame_acq_time']=0.1
time.sleep(2)

pos_list=[-136.06]

smpl_list_PDF=[5]  #PDF   #####

ScanPlans_PDF = 0   ######## 5

num_PDF = 1 #PDF	######## 4

temp_list=[180,200]

#PDF ###############################################for general measurement condition
glbl['frame_acq_time']=0.2   ########## 0.2
#move_PDF()
time.sleep(2) ### 10

for idx in range (len (temp_list)):
	RE(mv(eurotherm3504, temp_list[idx]))
	for num in range (num_PDF):
		print('moving temperature list', temp_list[idx])
		#RE(mv(OT_stage_2_X, pos_list[idx]))

		xrun(0,0, useful_info=measurement_data())
		print('sleep')
		glbl['frame_acq_time']=0.1
		time.sleep(2)    ### 20
		glbl['frame_acq_time']=0.2   ######## 0.2
		



glbl['frame_acq_time']=0.1
time.sleep(2)
glbl['frame_acq_time']=0.1
