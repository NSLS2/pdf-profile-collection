from epics import PV
from epics import caget, caput
import datetime
import numpy as np
import pylab
from pylab import *
import os
from tifffile import imsave,  imread
import sys


sample_posX = [-217]

sample_posY = [-121.05]  


sampleID_PDF = [0]

sampleID_XRD = [0]

# Number of images
num_repeat_PDF = 1
num_repeat_XRD = 1

frame_acq_time = 0.1


## ================================================================================##
ScanPlans_PDF = [5]*len(sampleID_PDF)   ######## 5
ScanPlans_XRD = [4]*len(sampleID_XRD)	######## 5

#Det_position
Det_PDF = 3070.0 #3022.5 #2810
Det_XRD = 3770.0 #3870.5 #3595

#wait time
wait_time_PDF = 60 #300	########
wait_time_XRD = 10 #300	########

if len(sampleID_PDF) == len(sample_posX) == len(sample_posY):
	print('\n Number of sampleID_PDF is consistent with sample_posX & sample_posY')
else:
	raise IndexError('\n Number of sampleID_PDF is NOT consistent with sample_posX & sample_posY')

if len(sampleID_XRD) == len(sample_posX) == len(sample_posY):
	print('\n Number of sampleID_XRD is consistent with sample_posX & sample_posY')
else:
	raise IndexError('\n Number of sampleID_XRD is NOT consistent with sample_posX & sample_posY')

print(f'\n *** Start to Measure PDF, {num_repeat_PDF = } \n')
move_PDF(Det_PDF)
for num in range(num_repeat_PDF):

	for i in range(len(sampleID_PDF)):
		print('\nmoving OT_stage_2_X', sample_posX[i])
		print('moving OT_stage_2_Y', sample_posY[i])
		print('Sample ID', sampleID_PDF[i], '\n')
		RE(mv(OT_stage_2_X, sample_posX[i], OT_stage_2_Y, sample_posY[i]))

		
		single_xrun(sampleID_PDF[i], ScanPlans_PDF[i], frame_time=frame_acq_time, 
					is_take_dark=True, use_flt1=False, use_flt2=False, use_flt3=False, 
					)
		
		print('\nSet frame time to 0.1 sec for sleep\n')
		glbl['frame_acq_time']=0.1
		tqdm_sleep(wait_time_PDF)    ### 20
		# glbl['frame_acq_time']=frame_acq_time   ######## 0.2


print(f'\n *** Start to Measure XRD, {num_repeat_XRD = } \n')
move_XRD(Det_XRD)
for num in range(num_repeat_XRD):
	
	for i in range(len(sampleID_XRD)):
		print('\nmoving OT_stage_2_X', sample_posX[i])
		print('moving OT_stage_2_Y', sample_posY[i])
		print('Sample ID', sampleID_XRD[i], '\n')
		RE(mv(OT_stage_2_X, sample_posX[i], OT_stage_2_Y, sample_posY[i]))

		
		single_xrun(sampleID_XRD[i], ScanPlans_XRD[i], frame_time=frame_acq_time, 
					is_take_dark=True, use_flt1=False, use_flt2=False, use_flt3=False, 
					)
		
		print('\nSet frame time to 0.1 sec for sleep\n')
		glbl['frame_acq_time']=0.1
		tqdm_sleep(wait_time_XRD)    ### 20
		# glbl['frame_acq_time']=frame_acq_time   ######## 0.2



