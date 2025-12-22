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

A = [450, 500, 550] + [600]*3 + [650] + [700]*3 + [30]

# A = [25, 28, 25]

T_threshold = 1	     	     # T-setpoint +-threshold
Settle_time = 60		     # Settle time after HAB reach the setpoint	Temperature

smpi_PDF = 8                # sample index for PDF
spi_PDF = 5                  # scan plan index for PDF
frame_time = 1.5            # frame acquisition time for PDF and XRD

smpi_XRD = 8                # for XRD
spi_XRD = 5                  # for XRD

glbl['frame_acq_time'] = 0.1   # Deatector frame acquasition time
glbl['dk_window'] = 30         # dark current acquasition window
st2 = 5                 	# sleep timebefore each measuement
temp_controller = hotairblower

#======================================= Definition of Measuremet =======================================
# Do not change anyhing below.  

i = 0
for t in A:
    
    RE(pbar_set_temp(temp_controller=temp_controller, setpoint=t, tolerance=T_threshold))

    tqdm_sleep(Settle_time, message='Wait for thermal equilibrium...')
    
    print('\nMove to PDF Setup\n')
    set_PDF()
    glbl['frame_acq_time'] = frame_time
    xrun(smpi_PDF, spi_PDF, more_info = measurement_data())
    glbl['frame_acq_time'] = 0.1
    tqdm_sleep(st2, message='Sleep and Change to XRD')

    print('\nMove to XRD Setup')
    set_XRD()
    glbl['frame_acq_time'] = frame_time
    xrun(smpi_XRD, spi_XRD, more_info = measurement_data())
    glbl['frame_acq_time'] = 0.1

    print('\nGo to next Temperature...\n')


