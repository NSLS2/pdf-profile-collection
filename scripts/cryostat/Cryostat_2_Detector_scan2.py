# Cryostat T-dependent XRD and PDF measurements
# Date Created: 02/09/2024(MA) 
# Last modified: 05/29/2026(KB)
import asyncio
import time
import numpy as np
import shutil
import matplotlib.pyplot as plt 
import os
import epics
N = np.nan
DEBUG = True

#------------------------------------------------- Definition of variables -----------------------------------------------
''' Change below variables as necessay  🤔🤔🤔 '''
A = [300]
B = list(range(5, 305, 10))
C = list(range(145, 0, -5 ))
D = list(range(10, 300, 5))
# B = [300]#np.arange(25, 305, 10)  #Uper limit excluded
#Tlist_2 = Tlist_1[::-1]
Tlist =  A 

"""Temp control settings"""
st = 0              # sleep time for Temperature stabiliy
st2 = 5             # sleep time before each measuement. this time will also be used to stabilize detector after changing frame acquisition time
Q_INTERVAL = 1  # Query interval for PID and temp setting
GIVE_UP = 10*60/Q_INTERVAL   # After this many seconds proceed with data collectoin even if perfect temp has not been acheived
MIN_FLAT_CNTS = 3 *60/Q_INTERVAL    # Min number of seconds a curve needs to be flat to move on

#S_X = [-681.84, -679.84, -673.74]
#      Cs2CdI2Cl2, Cs2SnI2Cl2, Ni
SMPI_PDF = [9,8,7,6,5,4,3,2,1]     # bt.list() Sample indices for PDF
SMPI_XRD = [29,28,27,26,25,24,23,22,21]     # bt.list() Sample indices for XRD
SPI_PDF = [6,12,11,14,6,6,6,6,7]        # bt.list() Scan plan indices for PDF
SPI_XRD = 9*[4]        # bt.list() Scan plan indices for XRD
FMT = 9*[0.1]  # Frame acquisition times for the samples. Set this value based on PDF requirement
OPTION = 9*[1]         # Measurement option for each sample 0: PDF & XRD, 1: PDF only, 2:XRD Only 
repeat = 4 ## XRD measurement repeats for 20 minuts at every temperature

my_config = {'auto_mask': False, 'qmaxinst':20, 'qmax':20, 'rpoly':0.95,
    'user_mask': '/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/Mask.npy',    
    'method': 'splitpixel'}

temp_controller = lakeshore336_2
#------------------------------------------= ''' Do not change anything  below !!!'''---------------------.move----------------
config_dir = "/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/" 
Time, T1, T2, Temperature, DetZ, SampleX, DI1, DI2, TCF, M_current = [],[],[],[],[],[],[],[],[],[] #TCF before measurement
#Tseries = lst(bt.samples.keys())[smpi] 

p_gain_pv = epics.PV("XF:28ID1-ES{LS336:1-Out:1}Gain:P-SP")
i_gain_pv = epics.PV("XF:28ID1-ES{LS336:1-Out:1}Gain:I-SP")
d_gain_pv = epics.PV("XF:28ID1-ES{LS336:1-Out:1}Gain:D-SP")

def sanity_check(t_list: list)->bool:
    """Return True if temperature list is insane"""
    return any(x > 500 for x in t_list)

def Figure(name: str) -> plt.figure:
    fig = plt.figure(name)
    ax = fig.gca()
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Temperature (K)")
    return fig

def set_PDF(): # Move PDF poni and mask files to config directory
    xpd_configuration['area_det']=pilatus1
    try:
        os.remove(os.path.join(config_dir, "xpdAcq_calib_info.poni"))
    except Exception:
        pass      
    shutil.copy(config_dir + "pilatus_PDF/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Exception:
        pass
    shutil.copy(config_dir + "pilatus_PDF/" + "Mask.npy" , config_dir)

def set_XRD(): # Move XRD poni and mask files to config directory
    xpd_configuration['area_det']=pe1c
    #Grid_X.move(0)
    Grid_Y.move(120)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass     
    shutil.copy(config_dir + "pe1c_XRD/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Exception:
        pass
    shutil.copy(config_dir + "pe1c_XRD/" + "Mask.npy" , config_dir)

# def change_T(t): # Cryostat chanel A setpoint loop
#     caput('XF:28ID1-ES{LS336:1-Out:1}T-SP',t)
#     while True:
#         tt =  temp_controller.read()['lakeshore336_temp_A_T']['value']
#         if t-1 <= tt <= t+1: # changed from +/- 0.3
#             break
#         else:
#             print(tt)
#         time.sleep(5)


async def measurement_data(): # .......Captures metadata   
    info_dict = {}
    info_dict['OT_stage_1_X'] = OT_stage_1_X.read()
    info_dict['OT_stage_1_Y'] = OT_stage_1_Y.read()
    info_dict['Det_1_X'] = Det_1_X.read()
    info_dict['Det_1_Y'] = Det_1_Y.read()
    info_dict['Det_1_Z'] = Det_1_Z.read()
    info_dict['Grid_X'] = Grid_X.read()
    info_dict['Grid_Y'] = Grid_Y.read()
    info_dict['Grid_Z'] = Grid_Z.read()
    info_dict['ring_current'] = ring_current.read()
    info_dict['frame_acq_time'] = glbl['frame_acq_time']
    info_dict['dk_window'] = glbl['dk_window']

    info_dict['cryostat_A_P'] = p_gain_pv.get()
    info_dict['cryostat_A_I'] = i_gain_pv.get()
    info_dict['cryostat_A_D'] = d_gain_pv.get()

    info_dict['cryostat_A'] = lakeshore336.read()['lakeshore336_temp_A_T']['value']
    info_dict['cryostat_A_V'] = caget('XF:28ID1-ES{LS336:1-Chan:A}Val:Sens-I')
    info_dict['cryostat_B'] = lakeshore336.read()['lakeshore336_temp_B_T']['value']
    info_dict['cryostat_B_V'] = caget('XF:28ID1-ES{LS336:1-Chan:B}Val:Sens-I')
    info_dict['cryostat_C'] = lakeshore336.read()['lakeshore336_temp_C_T']['value']
    info_dict['cryostat_C_V'] = caget('XF:28ID1-ES{LS336:1-Chan:C}Val:Sens-I')
    info_dict['cryostat_D'] = lakeshore336.read()['lakeshore336_temp_D_T']['value']
    info_dict['cryostat_D_V'] = caget('XF:28ID1-ES{LS336:1-Chan:D}Val:Sens-I')
    info_dict['Measurement_time'] = time.time()
    return info_dict

def Det_scan(SI, SP, repeat): # Pilatus three position scan
    for j in range(repeat):
        # det_x = [40.644, 31.356, 36]
        # det_y = [-3.356, -12.644, -8]
        # for i in range(len(det_x)):
        #     Grid_X.move(det_x[i])
        #     Grid_Y.move(det_y[i])
        #     #xrun(SI, jog([pilatus1], SP, OT_stage_2_Y, use_ypos-.5, use_ypos+.5), dark_strategy=no_dark,  more_info = useful_info())
        xrun(SI, SP, dark_strategy= no_dark, more_info = measurement_data(), user_config = my_config)


def measurement_PDF(figure: plt.figure): # PDF measurement 
    time_ = time.time()
    Time.append(time_)
    temperature = lakeshore336.read()['lakeshore336_temp_A_T']['value']
    temperature1 = lakeshore336.read()['lakeshore336_temp_B_T']['value']
    temperature2 = lakeshore336.read()['lakeshore336_temp_C_T']['value']
    temperature3 = lakeshore336.read()['lakeshore336_temp_D_T']['value']
    Det_scan(smpi,spi,repeat)  # Disable this in enable the previous line when 3 positions are not necessary
    ax = figure.gca()
    ax.plot((time_-Time[0])/3600,temperature, 'ro', markersize=.8)
    ax.plot((time_-Time[0])/3600,temperature1, 'go', markersize=.8)
    ax.plot((time_-Time[0])/3600,temperature2, 'bo', markersize=.8)
    ax.plot((time_-Time[0])/3600,temperature3, 'ko', markersize=.8)
    plt.ion()   
    plt.pause(0.05)

def measurement_XRD(): # XRD measurement
    time_ = time.time()
    Time.append(time_)
    temperature = lakeshore336.read()['lakeshore336_temp_C_T']['value']
    xrun(smpi, spi, more_info = measurement_data(), user_config = my_config) 


def shifter_T(motor: ophyd.device, temperature: float) -> list:
    #pos_list, I_list, peak_cen_list = scan_shifter_pos_ask(motor, -672.5, -691.5, 120, min_height=0.1, peak_rad=1.0)
    pos_list, I_list, peak_cen_list = scan_shifter_pos_ask(motor, -691, -672, 150, min_height=0.11, peak_rad=1.0)
    
    fn_scan = f'{motor.name}_{temperature}K_scan'
    fn_fitting = f'{motor.name}_{temperature}K_fitting'
    
    print('\noutput fitted peak position as csv file\n')
    fitting_pos_csv(peak_cen_list, save=True, fn_prefix=fn_fitting)
    
    print('\noutput scanned position, intensity profile as csv file\n')
    scan_pos_csv(pos_list, I_list, save=True, fn_prefix=fn_scan)

    return(peak_cen_list)


# ------------------------------------------- ''' Main T dependent Measurement loop '''' -----------------------------------------
for i in range(len(Tlist)):

    # This function changes an asynchronous device temp and 
    RE(move_and_continue(cryostat,Tlist[i]))

    S_X = shifter_T(OT_stage_1_X, Tlist[i])
    # time.sleep(st)
    tqdm_sleep(st, message='Waif for thermal equilibrium')

    temp_fig = Figure(temp_controller.name)
    if i == 0:
        # Figure()
        Time = []
    
    set_PDF()    
    for jj in range (len(S_X)):
        #glbl['frame_acq_time']= FMT[jj]
        time.sleep(st2)
        OT_stage_1_X.move(S_X[jj])
        spi_PDF = SPI_PDF[jj]
        spi_XRD = SPI_XRD[jj]
        smpi_PDF = SMPI_PDF[jj]
        smpi_XRD = SMPI_XRD[jj]
        option_1 = OPTION[jj]

        if option_1 == 0:   # PDF+XRD       
            spi = spi_PDF
            smpi = smpi_PDF
            measurement_PDF(temp_fig)
        elif option_1 == 1:
            spi = spi_PDF
            smpi = smpi_PDF
            measurement_PDF(temp_fig)
        else:
            pass

    set_XRD()    
    for kk in range (len(S_X)):
        #glbl['frame_acq_time']= FMT[kk]
        time.sleep(st2)
        OT_stage_1_X.move(S_X[kk])
        spi_PDF = SPI_PDF[kk]
        spi_XRD = SPI_XRD[kk]
        smpi_PDF = SMPI_PDF[kk]
        smpi_XRD = SMPI_XRD[kk]
        option_1 = OPTION[kk]

        if option_1 == 0:   # PDF+XRD       
            spi = spi_XRD
            smpi = smpi_XRD
            measurement_XRD()
        elif option_1 == 2:
            spi = spi_XRD
            smpi = smpi_XRD
            measurement_XRD()
        else:
            pass
            
'''
# -------Below part of the script insert metada in the headers of IQ, Itth, and Gr files in a way that pdfgui and GSAS-II can recognize and import-------
# meta_data function should be pre-defined by running "metadata_insert.py"
time.sleep(30)
for kk in range(len(SMPI_PDF)):
    try:
        meta_data(SMPI_PDF[kk])
        print(SMPI_PDF[kk])
    except Exception:
        pass
    
for ll in range(len(SMPI_XRD)):
    try:
        meta_data(SMPI_XRD[ll])
        print(SMPI_XRD[ll])
    except Exception:
        pass
        
'''