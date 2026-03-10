## Added by CHL on 2025/09/17

file_loading_timer.start()

import bluesky.plan_stubs as bps


# def check_setpoint(new_value, old_value, **kwargs):
#     if abs(new_value - T_from_sensor.get()) < tolerance:
#         # print(f'Reached setpoint {T_from_sensor.get()}.')
#         return True
#     return False


## RunEngine plan for cryostat
def cryostat_set_temp(temp_controller = lakeshore336_2, 
                      input_channel = 'temp.A', 
                      output_channel = 'out1', 
                      ramprate = 5, 
                      setpoint = 300, 
                      channel_range = 3, 
                      tolerance=0.5):
    
    new_temp = setpoint
    new_range = channel_range
    out_obj = getattr(temp_controller, output_channel)
    in_obj = getattr(temp_controller, input_channel)    
    T_from_sensor = in_obj.T
    start_T = T_from_sensor.get()

    def _check_setpoint(new_value, old_value, **kwargs):
        if abs(new_value - T_from_sensor.get()) < tolerance:
            # print(f'Reached setpoint {T_from_sensor.get()}.')
            return True
        return False
    
    print(f'\nSet {output_channel = } to temperature = {new_temp} K, using channel_range = {new_range}\n')
    yield from bps.mv(out_obj.range_selection, new_range, out_obj.ramprate, ramprate, out_obj.setpoint, new_temp)
    
    status = SubscriptionStatus(T_from_sensor, run=True, callback=_check_setpoint)

    status = temperature_pbar(start_T, out_obj.setpoint.get(), T_from_sensor, tolerance, status)
        
    return status

    
## RunEngine plan for eurotherm3504, hotairblower, linkam_T96
def pbar_set_temp(temp_controller = eurotherm3504, ramprate = 5, setpoint = 25, tolerance=0.5):

    ## for cs800 (cryostream), ramprate = 360
    ## for eurotherm3504 (flow cell), ramprate = 5

    new_temp = setpoint
    T_from_sensor = temp_controller.readback
    start_T = T_from_sensor.get()

    def _check_setpoint(new_value, old_value, **kwargs):
        if abs(new_value - T_from_sensor.get()) < tolerance:
            # print(f'Reached setpoint {T_from_sensor.get()}.')
            return True
        return False
    
    print(f'\nSet {temp_controller.name} to temperature = {new_temp} K, using ramp rate = {ramprate}\n')
    yield from bps.mv(temp_controller.ramprate, ramprate, temp_controller.setpoint, new_temp)

    ## for cs800 (cryostream), it needs to be triggered
    if temp_controller.name == 'cs800':
        yield from bps.mv(temp_controller.trig, 11)
        #wait 5 second to allow phaseID update after trigger
        tqdm_sleep(7, message='Wait after trigger')
        print('\n')
 
    status = SubscriptionStatus(T_from_sensor, run=True, callback=_check_setpoint)

    status = temperature_pbar(start_T, temp_controller.setpoint.get(), T_from_sensor, tolerance, status)
        
    return status

file_loading_timer.stop()