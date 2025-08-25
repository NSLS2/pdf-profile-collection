#Hui and Gihan modify this script on May 8, 2024.


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


def measurement_data(): # .......Captures metadata   
    info_dict = {}
    info_dict['OT_stage_2_X'] = OT_stage_2_X.read()
    info_dict['OT_stage_2_Y'] = OT_stage_2_Y.read()
    info_dict['Det_1_X'] = Det_1_X.read()
    info_dict['Det_1_Y'] = Det_1_Y.read()
    info_dict['Det_1_Z'] = Det_1_Z.read()
    info_dict['ring_current'] = ring_current.read()
    info_dict['frame_acq_time'] = glbl['frame_acq_time']
    info_dict['dk_window'] = glbl['dk_window']
    info_dict['Temperature'] = cryostream.T.get()
    info_dict['Measurement_time'] = time.time()
    return info_dict
config_dir = "/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/"
def move_PDF():
    Det_1_Z.move(D1)
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
    Det_1_Z.move(D2)
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

def one_rack_jog(smplist, posxlist, posy, exp_time, jogstart, jogstop, num_imgs=3, det_exp=0.5):
    '''
    ###--> want to measure sample at only a positon of y.
    posylist=[27]
    smplist=[[1,2,3,4]]  #requaiare double brackets [[ ]]
    for posy, smpl in zip(posylist, smplist):
         print(posy, smpl)
   
    27 [1, 2, 3, 4]
    '''
    #jog_motor = OT_stage_2_Y
    area_det = xpd_configuration['area_det']
    RE(mv(OT_stage_2_Y, posy))
    for num in range (num_PDF):
        for idx in range (len (posxlist)):
            print('moving OT_stage_2_X', posxlist[idx])
            RE(mv(OT_stage_2_X, posxlist[idx]))
            print(smplist[idx])
            plan = jog([area_det], exp_time, OT_stage_2_Y,jogstart, jogstop)
            xrun(smplist[idx], plan, more_info = measurement_data())
            print('sleep')
            glbl['frame_acq_time']=0.1
            time.sleep(1)    ### 90
            glbl['frame_acq_time']=det_exp_PDF   ######## 0.5        


def one_rack(smplist, posxlist, posy, ScanPlan, num_imgs, det_exp, spleeptime_btw_smpl):
    '''
    ###--> want to measure sample at only a positon of y.
    posylist=[27]
    smplist=[[1,2,3,4]]  #requaiare double brackets [[ ]]
    for posy, smpl in zip(posylist, smplist):
         print(posy, smpl)
     
    27 [1, 2, 3, 4]
    '''
    RE(mv(OT_stage_2_Y, posy))
    for num in range (num_imgs):
        for idx in range (len (posxlist)):
            print('moving OT_stage_2_X', posxlist[idx])
            RE(mv(OT_stage_2_X, posxlist[idx]))
            print(smplist[idx])

            xrun(smplist[idx], ScanPlan, more_info = measurement_data())
            print('sleep')
            glbl['frame_acq_time']=0.1
            time.sleep(spleeptime_btw_smpl)    ### 90
            glbl['frame_acq_time']=det_exp   ######## 0.5        


D1 = 4309   # Det_1_Z position for PDF
D2 = 4309 + 800 # Det_1_Z positio for XRD

pos_list_x1 = [-84, -85, -86, -87]   #####\
pos_list_x2 = [-84, -85, -86, -87]
pos_list_x3 = [-84, -85, -86, -87]

posy1 = -43
posy2 = -42
posy3 = -41

smpl_list_PDF_1=[0, 1, 0, 1]#PDF   #####
smpl_list_PDF_2=[0, 1, 0, 1]#PDF   #####
smpl_list_PDF_3=[0, 1, 0, 1] #PDF   #####

#detector exposure time
det_exp_PDF = 0.1  #0.5
det_exp_XRD = 1  #0.5

# image number
num_PDF = 2  #2
num_XRD = 2 

#Scanplan (ct_60,,,,)
ScanPlan_PDF = 4  #6 ct_60
ScanPlan_XRD = 5  #6 ct_120

#Sleep time between images
spleeptime_btw_smpl_PDF = 60  #unit: sec
spleeptime_btw_smpl_XRD = 60  #unit: sec

'''
#Air PDF
glbl['frame_acq_time']=2 #2$$$$$$  #PDF det exposure time #B_set $$$$$$$$$$$$$$$$
move_PDF()
RE(mv(OT_stage_2_X, -136.27))
for x in range(3):   #4
	xrun(110, 9, more_info = measurement_data())   #9
     
glbl['frame_acq_time']=0.1
time.sleep(120) ### 120
'''

###############################################################################===========================================================================
###example PDF and XRD
#take images at PDF detector position
move_PDF()
one_rack(smpl_list_PDF_1, pos_list_x1, posy1 , ScanPlan=ScanPlan_PDF, num_imgs=num_PDF, det_exp=det_exp_PDF, spleeptime_btw_smpl=spleeptime_btw_smpl_PDF)

glbl['frame_acq_time']=0.1
time.sleep(2)    ### 90

#take images at XRD detector position
move_XRD()
one_rack(smpl_list_PDF_1, pos_list_x1, posy1 , ScanPlan=ScanPlan_XRD, num_imgs=num_XRD, det_exp=det_exp_XRD, spleeptime_btw_smpl=spleeptime_btw_smpl_XRD)

glbl['frame_acq_time']=0.1
#####################################################################======================================================================================


#PDF1
glbl['frame_acq_time']=det_exp_PDF #2$$$$$$  #PDF det exposure time #B_set $$$$$$$$$$$$$$$$
#move_PDF()
time.sleep(2) ### 10


one_rack_jog(smpl_list_PDF_1, pos_list_x1, posy1 , 10, posy1, posy1+3, num_imgs=num_PDF, det_exp=det_exp_PDF)

'''

one_rack(smpl_list_PDF_1, pos_list_x1, posy1 , ScanPlan_PDF, num_PDF=num_PDF, det_exp_PDF=det_exp_PDF)
glbl['frame_acq_time']=0.1
time.sleep(2)    ### 90
one_rack(smpl_list_PDF_2, pos_list_x2, posy2 , ScanPlan_PDF, num_PDF=num_PDF, det_exp_PDF=det_exp_PDF)
glbl['frame_acq_time']=0.1
time.sleep(2)    ### 90
one_rack(smpl_list_PDF_3, pos_list_x3, posy3 , ScanPlan_PDF, num_PDF=num_PDF, det_exp_PDF=det_exp_PDF)

'''