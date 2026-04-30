from epics import PV
from epics import caget, caput
import datetime
import numpy as np
import pylab
from pylab import *
import os
from tifffile import imsave,  imread
import sys

Det_PDF = 2191.0   #Det_1_Z in bridge motion
Det_XRD = Det_PDF + 774   #2965



config_dir = "/nsls2/data/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/"

def move_PDF():
    Det_1_Z.move(Det_PDF)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass      
    shutil.copy(config_dir + "/pe1c_PDF/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Excemption:
        pass
    shutil.copy(config_dir + "/pe1c_PDF/" + "Mask.npy" , config_dir)

def move_XRD():
    Det_1_Z.move(Det_XRD)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass     
    shutil.copy(config_dir + "/pe1c_XRD/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Excemption:
        pass
    shutil.copy(config_dir + "/pe1c_XRD/" + "Mask.npy" , config_dir)


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

    # info_dict['cryostat_A'] = lakeshore336.read()['lakeshore336_temp_A_T']['value']
    # info_dict['cryostat_A_V'] = caget('XF:28ID1-ES{LS336:1-Chan:A}Val:Sens-I')
    # info_dict['cryostat_B'] = lakeshore336.read()['lakeshore336_temp_B_T']['value']
    # info_dict['cryostat_B_V'] = caget('XF:28ID1-ES{LS336:1-Chan:B}Val:Sens-I')
    # info_dict['cryostat_C'] = lakeshore336.read()['lakeshore336_temp_C_T']['value']
    # info_dict['cryostat_C_V'] = caget('XF:28ID1-ES{LS336:1-Chan:C}Val:Sens-I')
    # info_dict['cryostat_D'] = lakeshore336.read()['lakeshore336_temp_D_T']['value']
    # info_dict['cryostat_D_V'] = caget('XF:28ID1-ES{LS336:1-Chan:D}Val:Sens-I')

    # info_dict['hotairblower'] = hotairblower.read()['hotairblower']['value']
    # info_dict['linkam_T96'] = linkam_T96.readback.get()
    # info_dict['cryostream_T'] = cs800.read()['temperature']['value']
    # info_dict['eurotherm3504'] = eurotherm3504.read()['eurotherm3504']['value']



    info_dict['Measurement_time'] = time.time()

    return info_dict

