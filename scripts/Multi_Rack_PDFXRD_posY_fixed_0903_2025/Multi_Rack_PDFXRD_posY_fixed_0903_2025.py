from epics import PV
from epics import caget, caput
import datetime
import numpy as np
import pylab
from pylab import *
import os
from tifffile import imsave,  imread
import sys

# import importlib
# move_PDF = importlib.import_module("def_move_PDF_XRD_position").move_PDF
# move_XRD = importlib.import_module("def_move_PDF_XRD_position").move_XRD

CeO2_posX = -203.6314603


sample_posX_row1 = [-200.61715768, -197.67103235, -194.54956195, -191.63630728, 
                    -188.60735522, -185.60774388, -182.61126764, -179.63824033, -176.58765492, 
                    -173.55729932, -170.48123561, -167.67234344, -164.58035033, -161.61308123, 
                    -158.51562137, -155.53666413, -152.55319451, -149.51864389, -146.58311709, 
                    -143.4804359, -140.56947921, -137.53760529, -134.52084653, -131.52424238, 
                    ]


sample_posX_row2 = [-132.0035147, -135.01454682, -138.01021606, -140.92421229, -144.13111353, 
                    -146.94797508, -150.0190376, -153.04127056, -156.00363009, -159.15975515, 
                    -162.04245558, -164.93073012, -167.98137232, 
                    ]

sample_posX_row3 = [-159.10235516, -150.17423435, -141.14102875, -132.08282702]

posY = [-114.46, -50.06, 11.94]

posY = [-114.46, -50.06, 11.94]
sampleID_PDF_row1 = list(range(71, 47, -1))
sampleID_PDF_row2 = list(range(72, 85, 1))
sampleID_PDF_row3 = [88, 87, 86, 85]

sampleID_XRD_row1 = list(range(112, 88, -1))
sampleID_XRD_row2 = list(range(113, 126, 1))
sampleID_XRD_row3 = [129, 128, 127, 126]


#jog_plan = jog([area_det], exp_time, OT_stage_2_Y, jogstart, jogstop)
ScanPlans_PDF = [5, 5, 5]  #[5, jog_plan, jog_plan]   ######## Not good for all of the racks
ScanPlans_XRD = [5, 0, 0]	######## 5

# Number of images
num_repeat = 6

#Time to clear detector
wait_time_PDF = 60 #sec, time to clear detector after PDF measurement 
wait_time_XRD = 60 #sec, time to clear detector after XRD measurement 

#wait time for detector signal
wait_det_signal_PDF = 5 #sec
wait_det_signal_XRD = 5 #sec

#Det_position
Det_PDF = 3022.5 #2810
Det_XRD = 3870.5 #3595

frame_acq_time = 2


## ================================================================================##
glbl['frame_acq_time']= frame_acq_time
sample_posX = [sample_posX_row1, sample_posX_row2, sample_posX_row3]
sample_PDF_ID = [sampleID_PDF_row1, sampleID_PDF_row2, sampleID_PDF_row3]
sample_XRD_ID = [sampleID_XRD_row1, sampleID_XRD_row2, sampleID_XRD_row3]

for num in range(num_repeat):

	move_PDF(Det_PDF)
	for i in range(len(posY)):		#select rack in y-position
		for j in range(len(sample_PDF_ID[i])):		#scan x-position in the selected y-position (posY)
			print('\nmoving OT_stage_2_X', sample_posX[i][j])
			print('moving OT_stage_2_Y', posY[i])
			print('Sample ID', sample_PDF_ID[i][j], '\n')
			RE(mv(OT_stage_2_X, sample_posX[i][j], OT_stage_2_Y, posY[i]))
			# print([idx])

			xrun(sample_PDF_ID[i][j], ScanPlans_PDF[i])
			print('sleep')
			glbl['frame_acq_time']=0.1
			tqdm_sleep(wait_time_PDF, message='Clear detector after PDF')
			glbl['frame_acq_time']=frame_acq_time   ######## 0.2
			tqdm_sleep(wait_det_signal_PDF, message='wait time for detector signal')

	
	move_XRD(Det_XRD)
	for i in range(len(posY)):
		for j in range(len(sample_XRD_ID[i])):
			print('\nmoving OT_stage_2_X', sample_posX[i][j])
			print('moving OT_stage_2_Y', posY[i])
			print('Sample ID', sample_XRD_ID[i][j], '\n')
			RE(mv(OT_stage_2_X, sample_posX[i][j], OT_stage_2_Y, posY[i]))
			# print([idx])

			xrun(sample_XRD_ID[i][j], ScanPlans_XRD[i])
			print('sleep')
			glbl['frame_acq_time']=0.1
			tqdm_sleep(wait_time_XRD, message='Clear detector after XRD')
			glbl['frame_acq_time']=frame_acq_time   ######## 0.2
			tqdm_sleep(wait_det_signal_XRD, message='wait time for detector signal')



