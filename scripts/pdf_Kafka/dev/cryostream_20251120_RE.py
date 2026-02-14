
# posx = [ 44.4897294 , 35.17800453,  25.93901961,16.74604477]


# posx = [86.36610125, 53.97453757,]

# posy = [-155]

sample_ID_pdf = [10]

sample_ID_xrd = [11]

#scan_plan = [12, 9, 9, 12, 8, 8, 9, 9, 8, 8, 9, 9,  8, 9, 12, 12, 9, 9, 8, 9]

scan_plan_pdf = [7]

scan_plan_xrd = [8]

frame_time = [1.0]



temperature = [270, 240, 210, 180, 150, 120, 100, 270]
# temperature = [120, 100, 270]

rest_thermal = 60*5 ##seconds CHANGE

rest_PDF = 30  ##seconds CHANGE

rest_XRD = 10  ##seconds CHANGE

num_repeat1 = 1 # CHANGE

num_repeat2 = 1000 # CHANGE


def temperature_pdf(
        detector_config: dict,
        temperature_config: dict, 
        sample_ID: list = [0], 
        md: dict={}, 
        repeat: int = 1,
        rest: float = 2.0, 
                     ):
    """_summary_

    Args:
        detector_config (dict): _description_
        temperature_config (dict): _description_
        sample_ID (list, optional): _description_. Defaults to [0].
        md (dict, optional): _description_. Defaults to {}.
        repeat (int, optional): _description_. Defaults to 1.
        rest (float, optional): _description_. Defaults to 2.0.
    """
    
    det = detector_config['det']
    


    for i in range(repeat):

        for t in temperature:

            cs800.set_and_check(t)
            tqdm_sleep(rest_thermal, message='Wait for Thermal Equlibrium')

            set_pe1c_XRD()
            for j in range(len(sample_ID_xrd)):

                # x = posx[j]
                # y = posy[0]

                sample_name = bt.samples.sel(sample_ID_xrd[j])['sample_name']
                # print(f'\nmoving Multi_X, {x = }')
                # print(f'moving OT_stage_2_Y, {y = }')
                print(f'{sample_ID_xrd[j] = }, {sample_name = }\n')
                # RE(mv(Multi_X, x, OT_stage_2_Y, y))

                glbl['frame_acq_time'] = frame_time[0]
                tqdm_sleep(2)
                xrun(sample_ID_xrd[j], scan_plan_xrd[j], more_info=measurement_data())
                glbl['frame_acq_time'] = 0.1

                tqdm_sleep(rest_XRD, message='Sleep after a XRD measurement')
    
    
    pass



for i in range(num_repeat1):

    for t in temperature:

        cs800.set_and_check(t)
        tqdm_sleep(rest_thermal, message='Wait for Thermal Equlibrium')

        set_pe1c_XRD()
        for j in range(len(sample_ID_xrd)):

            # x = posx[j]
            # y = posy[0]

            sample_name = bt.samples.sel(sample_ID_xrd[j])['sample_name']
            # print(f'\nmoving Multi_X, {x = }')
            # print(f'moving OT_stage_2_Y, {y = }')
            print(f'{sample_ID_xrd[j] = }, {sample_name = }\n')
            # RE(mv(Multi_X, x, OT_stage_2_Y, y))

            glbl['frame_acq_time'] = frame_time[0]
            tqdm_sleep(2)
            xrun(sample_ID_xrd[j], scan_plan_xrd[j], more_info=measurement_data())
            glbl['frame_acq_time'] = 0.1

            tqdm_sleep(rest_XRD, message='Sleep after a XRD measurement')

        set_pe1c_PDF()
        for j in range(len(sample_ID_pdf)):

            # x = posx[j]
            # y = posy[0]

            sample_name = bt.samples.sel(sample_ID_pdf[j])['sample_name']
            # print(f'\nmoving Multi_X, {x = }')
            # print(f'moving OT_stage_2_Y, {y = }')
            print(f'{sample_ID_pdf[j] = }, {sample_name = }\n')
            # RE(mv(Multi_X, x, OT_stage_2_Y, y))

            glbl['frame_acq_time'] = frame_time[0]
            tqdm_sleep(2)
            xrun(sample_ID_pdf[j], scan_plan_pdf[j], more_info=measurement_data())
            glbl['frame_acq_time']=0.1

            tqdm_sleep(rest_PDF, message='Sleep after a PDF measurement')


# print('\n=============== Move to 2nd loop for holding 24 hours ================\n')

# for i in range(num_repeat2):

#     set_pe1c_XRD()
#     for j in range(len(sample_ID_xrd)):

#         # x = posx[j]
#         # y = posy[0]

#         sample_name = bt.samples.sel(sample_ID_xrd[j])['sample_name']
#         # print(f'\nmoving Multi_X, {x = }')
#         # print(f'moving OT_stage_2_Y, {y = }')
#         print(f'{sample_ID_xrd[j] = }, {sample_name = }\n')
#         # RE(mv(Multi_X, x, OT_stage_2_Y, y))

#         glbl['frame_acq_time'] = frame_time[0]
#         tqdm_sleep(2)
#         xrun(sample_ID_xrd[j], scan_plan_xrd[j], more_info=measurement_data())
#         glbl['frame_acq_time']=0.1

#         tqdm_sleep(rest_XRD, message='Sleep after a XRD measurement')


#     set_pe1c_PDF()
#     for j in range(len(sample_ID_pdf)):

#         # x = posx[j]
#         # y = posy[0]

#         sample_name = bt.samples.sel(sample_ID_pdf[j])['sample_name']
#         # print(f'\nmoving Multi_X, {x = }')
#         # print(f'moving OT_stage_2_Y, {y = }')
#         print(f'{sample_ID_pdf[j] = }, {sample_name = }\n')
#         # RE(mv(Multi_X, x, OT_stage_2_Y, y))

#         glbl['frame_acq_time'] = frame_time[0]
#         tqdm_sleep(2)
#         xrun(sample_ID_pdf[j], scan_plan_pdf[j], more_info=measurement_data())
#         glbl['frame_acq_time']=0.1

#         tqdm_sleep(rest_PDF, message='Sleep after a PDF measurement')