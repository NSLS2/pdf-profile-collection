from collections import deque
from ophyd import (EpicsMotor, PVPositioner, PVPositionerPC,
                           EpicsSignal, EpicsSignalRO, Device)
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FmtCpt
from ophyd import DynamicDeviceComponent as DDC
from ophyd import DeviceStatus, OrderedDict


file_loading_timer.start()

class Lakeshore336Setpoint(PVPositioner):
    readback = Cpt(EpicsSignalRO, 'T-RB')
    setpoint = Cpt(EpicsSignal, 'T-SP')
    done = Cpt(EpicsSignalRO, 'Sts:Ramp-Sts')
    ramp_enabled = Cpt(EpicsSignal, 'Enbl:Ramp-Sel')
    ramp_rate = Cpt(EpicsSignal, 'Val:Ramp-SP')
    p_gain = Cpt(EpicsSignal, 'Gain:P-RB', write_pv='Gain:P-SP')
    i_gain = Cpt(EpicsSignal, 'Gain:I-RB', write_pv='Gain:I-SP')
    d_gain = Cpt(EpicsSignal, 'Gain:D-RB', write_pv='Gain:D-SP')
    done_value = 0


class Lakeshore336Channel(Device):
    T = Cpt(EpicsSignalRO, 'T-I')
    V = Cpt(EpicsSignalRO, 'Val:Sens-I')
    status = Cpt(EpicsSignalRO, 'T-Sts')


def _temp_fields(chans, **kwargs):
    defn = OrderedDict()
    for c in chans:
        suffix = '-Chan:{}}}'.format(c)
        defn[c] = (Lakeshore336Channel, suffix, kwargs)
    return defn


class Lakeshore336(Device):
    temp = DDC(_temp_fields(['A','B','C','D']))
    out1 = Cpt(Lakeshore336Setpoint, '-Out:1}')
    out2 = Cpt(Lakeshore336Setpoint, '-Out:2}')
    out3 = Cpt(Lakeshore336Setpoint, '-Out:3}')
    out4 = Cpt(Lakeshore336Setpoint, '-Out:4}')                             


lakeshore336 = Lakeshore336('XF:28ID1-ES{LS336:1' , name='lakeshore336')



## The below Lakeshore objects are revised by CHL in order to fully control the device from ophyd level 

from ophyd.status import SubscriptionStatus, MoveStatus

def temperature_pbar(start_T, stop_T, T_callable, tolerance, status):
    from tqdm import tqdm

    if start_T > stop_T: ## ramping down
        tolerance = abs(tolerance) * -1
    elif start_T < stop_T: ## ramping up
        tolerance = abs(tolerance)
    else:
        pass

    with tqdm(total=100, desc=f'Target: {T_callable.get()}/{stop_T} K') as pbar:
        # percent_T = 0
        while not status.success:
            status.check_value(new_value=stop_T, old_value=T_callable.get())
            percent_T = round(100*abs((T_callable.get()-start_T)/(stop_T-tolerance-start_T)), 2)
            pbar.n = percent_T
            pbar.set_description(f'Target: {T_callable.get()}/{stop_T}\xB1{abs(tolerance)} K')
            pbar.refresh()
            time.sleep(2)
        
        print('\n################## Reach Target #######################\n')

    return status


class Lakeshore336Setpoint2(PVPositioner):
    setpoint = Cpt(EpicsSignal, 'T-SP')
    setpoint_readback = Cpt(EpicsSignalRO, 'T-RB')

    ramp_enabled = Cpt(EpicsSignal, 'Enbl:Ramp-Sel')
    ramprate = Cpt(EpicsSignal, 'Val:Ramp-SP')
    ramprate_readback = Cpt(EpicsSignalRO, 'Val:Ramp-RB')

    p_gain = Cpt(EpicsSignal, 'Gain:P-RB', write_pv='Gain:P-SP')
    i_gain = Cpt(EpicsSignal, 'Gain:I-RB', write_pv='Gain:I-SP')
    d_gain = Cpt(EpicsSignal, 'Gain:D-RB', write_pv='Gain:D-SP')

    done = Cpt(EpicsSignalRO, 'Sts:Ramp-Sts')
    done_value = 0

    set_max_val = Cpt(EpicsSignal, 'OUT:Max-SP')
    read_max_val = Cpt(EpicsSignalRO, 'OUT:Max-RB')

    # status = Cpt(EpicsSignalRO, 'Enbl-Sts')
    range_selection = Cpt(EpicsSignal, 'Val:Range-Sel')
    range_status = Cpt(EpicsSignalRO, 'Val:Range-Sts')

    def __init__(self, *args, setpoint_tolerance=1, **kwargs):

        # Sets tolerance for skipping `set` calls when already at setpoint.
        self.setpoint_tolerance = setpoint_tolerance
        super().__init__(*args, **kwargs)


    def set_setpoint(self, new_position, *args, timeout=None, wait=True, **kwargs):

        # Check if new setpoint is within setpoint_tolerance of setpoint redback, and if the controller is
        # at it's setpoint. If it is, return that the move was successful instantly to avoid lockup.
        if abs(self.setpoint_readback.get() - new_position) < self.setpoint_tolerance:
            return DeviceStatus(self, success=True, done=True)
        else:
            return super().set(new_position, *args, timeout=timeout, wait=wait, **kwargs)


    def select_range(self, new_range, *args, timeout=None, wait=True, **kwargs):

        # Check if range_selection is same as range_status, and if the controller is
        # at it's setpoint. If it is, return that the move was successful instantly to avoid lockup.
        if self.range_status.get() == new_range:
            return DeviceStatus(self, success=True, done=True)
        else:
            # return super().set(new_range, *args, timeout=timeout, wait=wait, **kwargs)
            return self.range_selection.put(new_range)


class Lakeshore336_2(Device):
    temp = DDC(_temp_fields(['A','B','C','D']))
    out1 = Cpt(Lakeshore336Setpoint2, '-Out:1}')
    out2 = Cpt(Lakeshore336Setpoint2, '-Out:2}')
    out3 = Cpt(Lakeshore336Setpoint2, '-Out:3}')
    out4 = Cpt(Lakeshore336Setpoint2, '-Out:4}')

    def __init__(self, *args, tolerance=0.5, **kwargs):
        self.tolerance = tolerance
        super().__init__(*args, **kwargs)

    def set_and_check(self, new_value, new_range, input_channel='temp.A', output_channel='out1'):
        out_obj = getattr(self, output_channel)
        in_obj = getattr(self, input_channel)
        T_from_sensor = in_obj.T
        start_T = T_from_sensor.get()
        
        def _check_setpoint(*, new_value, old_value, **kwargs):
            if abs(new_value - T_from_sensor.get()) < self.tolerance:
                # print(f'Reached setpoint {T_from_sensor.get()}.')
                return True
            return False

        print(f'\nSet {output_channel = } to temperature = {new_value} K, using channel_range = {new_range}\n')
        out_obj.select_range(new_range, wait=False)
        out_obj.set_setpoint(new_value, wait=False)
        status = SubscriptionStatus(T_from_sensor, run=True, callback=_check_setpoint)

        status = temperature_pbar(start_T, out_obj.setpoint.get(), T_from_sensor, self.tolerance, status)

        return status



lakeshore336_2 = Lakeshore336_2('XF:28ID1-ES{LS336:1' , name='lakeshore336_2')

file_loading_timer.stop()