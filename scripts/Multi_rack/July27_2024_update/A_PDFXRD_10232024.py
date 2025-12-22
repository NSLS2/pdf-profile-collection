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

config_dir = "/nsls2/data/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/"

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

def move_PDF():
    Det_1_Z.move(D1)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass      
    shutil.copy(config_dir + "/PDF/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Exception:
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
    except Exception:
        pass
    shutil.copy(config_dir + "/XRD/" + "Mask.npy" , config_dir)


def one_rack_jog(smplist, posxlist, posylist, exp_time, jogstart, jogstop, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep):
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

    for num in range (num_imgs):
        for idx in range (len (posxlist)):
            print('moving OT_stage_2_X', posxlist[idx])
            print('moving OT_stage_2_Y', posylist[idx])
            RE(mv(OT_stage_2_X, posxlist[idx]))
            RE(mv(OT_stage_2_Y, posylist[idx]))
            print(smplist[idx])
            plan = jog([area_det], exp_time, OT_stage_2_Y, jogstart, jogstop)
            xrun(smplist[idx], plan, more_info = measurement_data())
            print('sleep')
            glbl['frame_acq_time']=0.1
            time.sleep(sleeptime_btw_smpl)    ### 90
            glbl['frame_acq_time']=det_exp_for_sleep   ######## 0.5        

def one_rack_jog_rel(smplist, posxlist, posylist, exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep):
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

    for num in range (num_imgs):
        for idx in range (len (posxlist)):
            print('moving OT_stage_2_X', posxlist[idx])
            print('moving OT_stage_2_Y', posylist[idx])
            RE(mv(OT_stage_2_X, posxlist[idx]))
            RE(mv(OT_stage_2_Y, posylist[idx]))
            print(smplist[idx])
            jogstart = posylist[idx]-jog_dist
            jogstop = posylist[idx] +jog_dist
            plan = jog([area_det], exp_time, OT_stage_2_Y, jogstart, jogstop)
            xrun(smplist[idx], plan, more_info = measurement_data())
            print('sleep')
            glbl['frame_acq_time']=0.1
            time.sleep(sleeptime_btw_smpl)    ### 90
            glbl['frame_acq_time']=det_exp_for_sleep   ######## 0.5  


# #def one_rack(smplist, posxlist, posy, ScanPlan, num_imgs, det_exp, sleeptime_btw_smpl):
#     '''
#     ###--> want to measure sample at only a positon of y.
#     posylist=[27]
#     smplist=[[1,2,3,4]]  #requaiare double brackets [[ ]]
#     for posy, smpl in zip(posylist, smplist):
#          print(posy, smpl)
     
#     27 [1, 2, 3, 4]
#     '''
#     RE(mv(OT_stage_2_Y, posy))
#     for num in range (num_imgs):
#         for idx in range (len (posxlist)):
#             print('moving OT_stage_2_X', posxlist[idx])
#             RE(mv(OT_stage_2_X, posxlist[idx]))
#             print(smplist[idx])

#             xrun(smplist[idx], ScanPlan, more_info = measurement_data())
#             print('sleep')
#             glbl['frame_acq_time']=0.1
#             time.sleep(sleeptime_btw_smpl)    ### 60
#             glbl['frame_acq_time']=det_exp   ######## 0.2        


D1 = 3011   # Det_1_Z position for PDF
D2 = 3011 + 777 # Det_1_Z positio for XRD



'''
pos_list_x1 = [-84, -85, -86, -87]   #####
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



# total number of images
num_PDF = 2  #2
num_XRD = 2 

#Scanplan (ct_60,,,,)
ScanPlan_PDF = 4  #6 ct_60
ScanPlan_XRD = 5  #6 ct_120

#Sleep time between images
spleeptime_btw_smpl_PDF = 60  #unit: sec
spleeptime_btw_smpl_XRD = 60  #unit: sec

'''

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


def jog(dets, exposure_s, motor, start, stop, md=None):
    """pass total exposure time (in seconds), motor name (i.e. Grid_Y), start and stop positions for the motor."""
    # yield from rocking_ct([pilatus], exposure_s, motor, start, stop)
    yield from rocking_ct(dets, exposure_s, motor, start, stop, md=md)

scan_time= total exposure time (sec)
    
xrun(0,jog([pe1c],scan_time, ystage, ymin, ymax), more_info = measurement_data())

one_rack_jog(smpl_list_PDF_1, pos_list_x1, posy1 , 10, posy1, posy1+3, num_imgs=num_PDF, det_exp=det_exp_PDF)

'''

'''
#emptykapton tape PDF
glbl['frame_acq_time']=2 #2   $$$$$$  #PDF det exposure time #B_set $$$$$$$$$$$$$$$$
move_PDF()
RE(mv(OT_stage_2_X, -191.3))
RE(mv(OT_stage_2_Y, 66))

for x in range(3):   #3
	xrun(36, 5, more_info = measurement_data())   #5
     
glbl['frame_acq_time']=0.1
time.sleep(60) ### 60
'''

#toprack1
#PDF measurement
#high Intensity sample

glbl['frame_acq_time'] = 0.1   #0.1

smpl_list_PDF_1 = [553,  555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 
                    565, 566, 567, 568, 569, 570, 571, 572, 575, 576, 
                    577, 578, 579, 580, 581, 582, 583]

smpl_list_PDF_2=[553, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 
                  565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 
                  577, 578, 579, 580, 581, 582, 583]

#                  185,184,183,182,181,180,179,178,177,176,
#                  175,174,173,172,171,170,169,168,167,166,
#                  165]

smpl_list_PDF_3=[554]

# smpl_list_PDF_4=[255,254,253,252,251,250,249,248,247,246,
#                  245,244,243,242,241,240,239,238,237,236,
#                  235,234,233,232,231,230,229,228,227]

#smpl_list_XRD_1=[543,544,545,546,547,548]
pos_list_x1 = [-132.24,  -137.93, -141.39, -144.11, -146.72, -150.11,
       -153.02, -156.11, -159.19, -162.52, -165.33, -168.3 , -171.2 ,
       -174.19, -177.41, -180.22, -183.06, -186.33, 
       -195.41, -198.13, -201.14, -204.31, -207.21, -210.37, -213.37,
       -216.49, -219.46, -222.24]
pos_list_y1 = [61.86,61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 
            61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 
            61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 61.86, 61.86]
            
#please use pos_list_y1 = [61.86]*10

# smpl_list_XRD_2=[551,552]
pos_list_x2 = [-132.24,  -137.93, -141.39, -144.11, -146.72, -150.11,
       -153.02, -156.11, -159.19, -162.52, -165.33, -168.3 , -171.2 ,
       -174.19, -177.41, -180.22, -183.06, -186.33,-189.28, -192.28,
       -195.41, -198.13, -201.14, -204.31, -207.21, -210.37, -213.37,
       -216.49, -219.46, -222.24]
pos_list_y2 = [70.86,70.86,70.86,70.86,70.86,70.86,70.86,70.86,70.86,
               70.86,70.86,70.86,70.86,70.86,70.86,70.86,70.86,70.86,70.86,
               70.86,70.86,70.86,70.86,70.86,70.86,70.86,70.86,70.86,70.86,
               70.86]
# smpl_list_XRD_3=[513, 514, 515, 516, 517, 518, 519, 520]
pos_list_x3 = [-134.95]
pos_list_y3 = [61.86]
# smpl_list_XRD_4=[521, 522, 523, 524, 525, 526, 527, 528, 529]
# pos_list_x4 = [-132.8,-143.8,-154.9,-165.9,-176.9,-187.9,-198.9,-209.8,-220.8]
# pos_list_y4 = [2.36,2.36,2.36,2.36,2.36,2.36,2.36,2.36,2.36]
# smpl_list_XRD_5=[530, 531, 532, 533, 534, 535, 536, 537, 538]
# pos_list_x5 = [-132.1,-143.1,-154.1,-166.1,-178.1,-190.1,-201.1,-212.1,-222.1]
# pos_list_y5 = [35.36,35.36,35.36,35.36,35.36,35.36,35.36,35.36,35.36]
# smpl_list_XRD_6=[539, 540, 541, 542]
# pos_list_x6 = [-134.1,-145.1,-156.1,-170.1]
# pos_list_y6 = [66.36,66.36,66.36,66.36]

print(len(smpl_list_PDF_2),len(pos_list_x2),len(pos_list_y2))
print(len(smpl_list_PDF_1),len(pos_list_x1),len(pos_list_y1))
# print(len(smpl_list_XRD_3),len(pos_list_x3),len(pos_list_y3))
# print(len(smpl_list_XRD_4),len(pos_list_x4),len(pos_list_y4))
# print(len(smpl_list_XRD_5),len(pos_list_x5),len(pos_list_y5))
# print(len(smpl_list_XRD_6),len(pos_list_x6),len(pos_list_y6))


total_exp_time_rack1 = 600   #30    total exposure time
num_PDF_rack1 = 1        #1  number of images   
det_exp_PDF_rack1 = 0.2      #0.1  detector exposure time
sleeptime_btw_smpl_rack1 = 120   #60

jog_dist = 0

total_exp_time=total_exp_time_rack1
num_imgs=num_PDF_rack1
det_exp_for_sleep=det_exp_PDF_rack1
sleeptime_btw_smpl=sleeptime_btw_smpl_rack1
sleeptime_btw_smpl, det_exp_for_sleep

print("exposure time =", total_exp_time,
      "sleep between samples =", sleeptime_btw_smpl, 
      "setector exposure time =", det_exp_for_sleep,
      "jog_dist =", jog_dist )

move_PDF()
#rack1
#one_rack_jog_rel(smpl_list_PDF_3, pos_list_x3, pos_list_y3 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

# #rack2
one_rack_jog_rel(smpl_list_PDF_2, pos_list_x2, pos_list_y2 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

# #rack3
one_rack_jog_rel(smpl_list_PDF_1, pos_list_x1, pos_list_y1 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)


one_rack_jog_rel(smpl_list_PDF_2, pos_list_x2, pos_list_y2 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

# #rack3
one_rack_jog_rel(smpl_list_PDF_1, pos_list_x1, pos_list_y1 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

# #rack4
# one_rack_jog_rel(smpl_list_PDF_4, pos_list_x4, pos_list_y4 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)


#glbl['frame_acq_time']=0.1
#time.sleep(60) ### 60


#move_XRD()
# total_exp_time_rack1 = 60 #60   redefine exp time to 60 for xrd
# total_exp_time=total_exp_time_rack1

#emptykapton tape XRD
# glbl['frame_acq_time']=2 #2$$$$$$  #PDF det exposure time #B_set $$$$$$$$$$$$$$$$
# RE(mv(OT_stage_2_X, -191.3))
# RE(mv(OT_stage_2_Y, 66))

# for x in range(3):   #3
# 	xrun(71, 5, more_info = measurement_data())   #5
     
# glbl['frame_acq_time']=0.5
# time.sleep(60) ### 60

# det_exp_XRD_rack1 = 0.1
# det_exp_for_sleep=det_exp_XRD_rack1

# print("exposure time =", total_exp_time,
#       "sleep between samples =", sleeptime_btw_smpl, 
#       "setector exposure time =", det_exp_for_sleep,
#       "jog_dist =", jog_dist)

# #rack1
# one_rack_jog_rel(smpl_list_XRD_1, pos_list_x1, pos_list_y1 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

# # #rack2
# one_rack_jog_rel(smpl_list_XRD_2, pos_list_x2, pos_list_y2 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

# #rack3
#one_rack_jog_rel(smpl_list_XRD_3, pos_list_x3, pos_list_y3 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

# #rack4
#one_rack_jog_rel(smpl_list_XRD_4, pos_list_x4, pos_list_y4 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

#rack5
#one_rack_jog_rel(smpl_list_XRD_5, pos_list_x5, pos_list_y5 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

#rack6
#one_rack_jog_rel(smpl_list_XRD_6, pos_list_x6, pos_list_y6 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)


#Toprack1:
#emptykaptpn=-131.72 @Y 60.0
#1st:emptykapton
#2nd: LaB6, X: -134.69
#3nd: Ni

# [-131.71, -134.69, -137.7 , -140.71, -143.73, -146.72, -149.74,
#        -152.77, -155.76, -158.75, -161.78, -164.76, -167.75, -170.78,
#        -173.78, -176.78, -179.8 , -182.82, -185.78, -188.8 , -191.82,
#        -194.81, -197.85, -200.83, -203.85, -206.83, -209.83, -212.82,
#        -215.84, -218.85, -221.81])



glbl['frame_acq_time']=0.1
glbl['frame_acq_time']=0.1



#######Did you check the intensity of spotty area?
####### intensity is higher than 60k.
#####please reduce detector exposure time or using filters if detectro exposure time higher than 0.1.


