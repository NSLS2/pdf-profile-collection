from epics import PV
from epics import caget, caput
import datetime
import numpy as np
import pylab
from pylab import *
import os
from tifffile import imsave,  imread
import sys


Det_PDF = 3070
Det_XRD = 3770


config_dir = "/nsls2/data/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/"
#data_dir = "/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/tiff_base/" + str(Tseries) + "/dark_sub/"   #for linkam
#data_dir_2 = "/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/tiff_base/" + str(Tseries) + "/integration/"  #for linkam

def move_PDF():
    Det_1_Z.move(Det_PDF)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass      
    shutil.copy(config_dir + "/PDF/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Excemption:
        pass
    shutil.copy(config_dir + "/PDF/" + "Mask.npy" , config_dir)

def move_XRD():
    Det_1_Z.move(Det_XRD)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass     
    shutil.copy(config_dir + "/XRD/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Excemption:
        pass
    shutil.copy(config_dir + "/XRD/" + "Mask.npy" , config_dir)


def measurement_data(): # .......Captures metadata   
    info_dict = {}
    info_dict['OT_stage_1_X'] = OT_stage_1_X.read()
    info_dict['OT_stage_1_Y'] = OT_stage_1_Y.read()
    info_dict['OT_stage_2_X'] = OT_stage_2_X.read()
    info_dict['OT_stage_2_Y'] = OT_stage_2_Y.read()
    info_dict['Det_1_X'] = Det_1_X.read()
    info_dict['Det_1_Y'] = Det_1_Y.read()
    info_dict['Det_1_Z'] = Det_1_Z.read()
    info_dict['Grid_X'] = Grid_X.read()
    info_dict['Grid_Y'] = Grid_Y.read()
    info_dict['Grid_Z'] = Grid_Z.read()
    info_dict['ring_current'] = ring_current.read()
    info_dict['frame_acq_time'] = glbl['frame_acq_time']
    info_dict['dk_window'] = glbl['dk_window']
    info_dict['cryostat_A'] = lakeshore336.read()['lakeshore336_temp_A_T']['value']
    info_dict['cryostat_B'] = lakeshore336.read()['lakeshore336_temp_B_T']['value']
    info_dict['cryostat_C'] = lakeshore336.read()['lakeshore336_temp_C_T']['value']
    info_dict['cryostat_D'] = lakeshore336.read()['lakeshore336_temp_D_T']['value']
    info_dict['Measurement_time'] = time.time()
    info_dict['linkam_T96_readback_get'] = linkam_T96.readback.get()
    info_dict['linkam_T96_temperature_get'] = linkam_T96.temperature.get()
    info_dict['linkam_T96_setpoint_set_get'] = linkam_T96.setpoint.get()
    info_dict['cryostream_T'] = cryostream.T.read()
    info_dict['eurotherm3504_get'] = eurotherm3504.get()
    info_dict['hotairblower_get'] = hotairblower.get()
    
    return info_dict