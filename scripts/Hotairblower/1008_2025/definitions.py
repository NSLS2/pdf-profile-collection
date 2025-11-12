
temp_controller = lakeshore336_2
#------------------------------------------= ''' Do not change anything  below !!!'''---------------------.move----------------
config_dir = "/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/" 


def set_PDF(): # Move PDF poni and mask files to config directory
    xpd_configuration['area_det']=pilatus1
    Grid_Z.move(1972)
    # xpd_configuration['area_det']=pe1c
    # Det_1_Z.move(2679)

    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass      
    shutil.copy(config_dir + "/pilatus_PDF/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Exception:
        pass
    shutil.copy(config_dir + "/pilatus_PDF/" + "Mask.npy" , config_dir)

def set_XRD(): # Move XRD poni and mask files to config directory
    # xpd_configuration['area_det']=pe1c
    # Det_1_Z.move(2679+700)
    xpd_configuration['area_det']=pilatus1
    Grid_Z.move(1972+700)

    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass     
    shutil.copy(config_dir + "/pilatus_XRD/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Exception:
        pass
    shutil.copy(config_dir + "/pilatus_XRD/" + "Mask.npy" , config_dir)


## run the following commmand before using scan_shifter_pos(OT_stage_2_X, -128, -218, 400)
def set_scan_pos():
    Grid_X.move(0)
    Grid_Y.move(130)

    xpd_configuration['area_det']=pe1c
    glbl['frame_acq_time']=0.1



def measurement_data(): # .......Captures metadata   
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
    # info_dict['cryostat_A'] = lakeshore336.read()['lakeshore336_temp_A_T']['value']
    # info_dict['cryostat_A_V'] = caget('XF:28ID1-ES{LS336:1-Chan:A}Val:Sens-I')
    # info_dict['cryostat_B'] = lakeshore336.read()['lakeshore336_temp_B_T']['value']
    # info_dict['cryostat_B_V'] = caget('XF:28ID1-ES{LS336:1-Chan:B}Val:Sens-I')
    # info_dict['cryostat_C'] = lakeshore336.read()['lakeshore336_temp_C_T']['value']
    # info_dict['cryostat_C_V'] = caget('XF:28ID1-ES{LS336:1-Chan:C}Val:Sens-I')
    # info_dict['cryostat_D'] = lakeshore336.read()['lakeshore336_temp_D_T']['value']
    # info_dict['cryostat_D_V'] = caget('XF:28ID1-ES{LS336:1-Chan:D}Val:Sens-I')
    # info_dict['hotairblower'] = hotairblower.read()['hotairblower_readback']['value']
    info_dict['Measurement_time'] = time.time()
    return info_dict

# def Det_scan(SI, SP, repeat): # Pilatus three position scan
#     for j in range(repeat):
#         # det_x = [40.644, 31.356, 36]
#         # det_y = [-3.356, -12.644, -8]
#         # for i in range(len(det_x)):
#         #     Grid_X.move(det_x[i])
#         #     Grid_Y.move(det_y[i])
#         #     #xrun(SI, jog([pilatus1], SP, OT_stage_2_Y, use_ypos-.5, use_ypos+.5), dark_strategy=no_dark,  more_info = useful_info())
#         xrun(SI, SP, dark_strategy= no_dark, more_info = measurement_data(), user_config = my_config)




