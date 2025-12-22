from tqdm import tqdm


def tqdm_sleep(rest_time, message='Sleep'):
    from tqdm import tqdm
    for j in tqdm(range(0,100), desc=message):
        time.sleep(rest_time/100)



def multi_xrun(sample_ID, scanplan, num_scan, frame_time=0.1, rest_time=60, is_take_dark=True, 
               use_flt1=False, use_flt2=False, use_flt3=False, 
               ):
    
    if use_flt1:
        RE(mv(fb_two_button_shutters.flt1, 0))

    else:
        RE(mv(fb_two_button_shutters.flt1, 1))

    if use_flt2:
        RE(mv(fb_two_button_shutters.flt2, 0))

    else:
        RE(mv(fb_two_button_shutters.flt2, 1))

    if use_flt3:
        RE(mv(fb_two_button_shutters.flt3, 0))

    else:
        RE(mv(fb_two_button_shutters.flt3, 1))

    
    glbl['frame_acq_time']=frame_time

    if is_take_dark:
        print('\nSet dark window to 0.1 min\n')
        glbl['dk_window'] = 0.1

    else:
        print('\nSet dark window to 1000 min\n')
        glbl['dk_window'] = 1000
    
    for i in range(num_scan):

        xrun(sample_ID, scanplan)

        print('\nSet frame time to 0.1 sec for sleep\n')
        glbl['dk_window'] = 0.1
        glbl['frame_acq_time']=0.1

        # for j in tqdm(range(0,100), desc='Sleep'):
        #     time.sleep(rest_time/100)
        tqdm_sleep(rest_time)


        print(f'\nSet frame time to back to {frame_time} sec\n')
        glbl['frame_acq_time']=frame_time


    print('\n*** Scan complete ***\n')
    RE(mv(fb_two_button_shutters.flt1, 1))
    RE(mv(fb_two_button_shutters.flt2, 1))
    RE(mv(fb_two_button_shutters.flt3, 1))

    print('\nSet dark window to 0.1 min\n')
    glbl['dk_window'] = 0.1
    print('\nSet frame time to 0.1 sec\n')
    glbl['frame_acq_time']=0.1




def single_xrun(sample_ID, scanplan, frame_time=0.1, is_take_dark=True, 
               use_flt1=False, use_flt2=False, use_flt3=False, 
               ):
    
    if use_flt1:
        RE(mv(fb_two_button_shutters.flt1, 0))

    else:
        RE(mv(fb_two_button_shutters.flt1, 1))

    if use_flt2:
        RE(mv(fb_two_button_shutters.flt2, 0))

    else:
        RE(mv(fb_two_button_shutters.flt2, 1))

    if use_flt3:
        RE(mv(fb_two_button_shutters.flt3, 0))

    else:
        RE(mv(fb_two_button_shutters.flt3, 1))

    
    glbl['frame_acq_time']=frame_time

    if is_take_dark:
        print('\nSet dark window to 0.1 min\n')
        glbl['dk_window'] = 0.1

    else:
        print('\nSet dark window to 1000 min\n')
        glbl['dk_window'] = 1000
    


    xrun(sample_ID, scanplan)

    print('\n*** Scan complete ***\n')
    RE(mv(fb_two_button_shutters.flt1, 1))
    RE(mv(fb_two_button_shutters.flt2, 1))
    RE(mv(fb_two_button_shutters.flt3, 1))

    # print('\nSet dark window to 0.1 min\n')
    # print('\nSet frame time to 0.1 sec for sleep\n')
    glbl['dk_window'] = 0.1
    glbl['frame_acq_time']=0.1
