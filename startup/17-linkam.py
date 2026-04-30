#added by Gihan/Hui for Linkam T96 on 02/18/2025
#This is working. Minimum temp is about 25oC.
######useful command for Linkam_T96
#linkam_T96.ramprate.get(), or linkam_T96.ramprate.set(target_ramprate)
#linkam_T96.setpoint.set(target_temp)
#linkam_T96.readback.get()  or linkam_T96.temperature.get()
#linkam_T96.move(target_temp)
####RE(mv(linkam_T96, target_temp)) is "not working" on 2/20/2025

file_loading_timer.start()


## Revised by CHL on 2025/09/17
class LinkamFurnace_T96(PVPositioner):
    
    def __init__(self, *args, setpoint_tolerance=1, **kwargs):
        
        # Sets tolerance for skipping `set` calls when already at setpoint.
        self.setpoint_tolerance = setpoint_tolerance
        super().__init__(*args, **kwargs)


    setpoint = Cpt(EpicsSignal, 'SETPOINT:SET', kind='normal')
    setpoint_readback = Cpt(EpicsSignalRO, 'SETPOINT', kind='hinted')

    done = Cpt(EpicsSignalRO, 'STATUS')
    stop_signal = Cpt(EpicsSignal, 'STATUS')
    
    readback = Cpt(EpicsSignalRO, 'TEMP', kind='hinted')
    temperature = Cpt(EpicsSignalRO, 'TEMP', kind='hinted')
    
    ramprate = Cpt(EpicsSignal, 'RAMPRATE:SET', kind='normal')
    ramprate_readback = Cpt(EpicsSignalRO, 'RAMPRATE', kind='hinted')

    on_off = Cpt(EpicsSignal, 'STARTHEAT', kind='normal')


    def set(self, new_position, *args, timeout=None, **kwargs):

        # Check if new setpoint is within one degree of current temperature, and if the controller is
        # at it's setpoint. If it is, return that the move was successful instantly to avoid lockup.
        if abs(self.readback.get() - new_position) < self.setpoint_tolerance and self.status.get() & 4 == 1:
            return DeviceStatus(self, success=True, done=True)
        else:
            return super().set(*args, timeout=timeout, **kwargs)

    def trigger(self):
        # There is nothing to do. Just report that we are done.
        # Note: This really should not necessary to do --
        # future changes to PVPositioner may obviate this code.
        status = DeviceStatus(self)
        status._finished()
        return status


linkam_T96 = LinkamFurnace_T96('XF:28ID1-ES{LINKAM:T96}:',name='linkam_T96',settle_time=0)
linkam_T96.done_value = 22
linkam_T96.stop_value = 22
linkam_T96.readback.kind = "normal"
linkam_T96.readback.name = 'temperature'
linkam_T96.setpoint.name = 'temperature_setpoint'
linkam_T96.ramprate.name = 'ramprate'



'''
linkam_T96
XF:28ID1-ES{LINKAM:T96}:CONFIG
XF:28ID1-ES{LINKAM:T96}:CTRLLR:ERR
XF:28ID1-ES{LINKAM:T96}:DISABLE
XF:28ID1-ES{LINKAM:T96}:DSC
XF:28ID1-ES{LINKAM:T96}:LNP_MODE:SET
XF:28ID1-ES{LINKAM:T96}:LNP_SPEED
XF:28ID1-ES{LINKAM:T96}:LNP_SPEED:SET
XF:28ID1-ES{LINKAM:T96}:MODEL
XF:28ID1-ES{LINKAM:T96}:POWER
XF:28ID1-ES{LINKAM:T96}:RAMPRATE
XF:28ID1-ES{LINKAM:T96}:RAMPRATE:SET
XF:28ID1-ES{LINKAM:T96}:RAMPTIME
XF:28ID1-ES{LINKAM:T96}:SETPOINT
XF:28ID1-ES{LINKAM:T96}:SETPOINT:SET
XF:28ID1-ES{LINKAM:T96}:STAGE:CONFIG
XF:28ID1-ES{LINKAM:T96}:STAGE:MODEL
XF:28ID1-ES{LINKAM:T96}:STARTHEAT
XF:28ID1-ES{LINKAM:T96}:STATUS
XF:28ID1-ES{LINKAM:T96}:TEMP
XF:28ID1-ES{LINKAM:T96}:WATER_PUMP_CMD
XF:28ID1-ES{LINKAM:T96}:WATER_PUMP_CURRENT
XF:28ID1-ES{LINKAM:T96}:WATER_PUMP_RPM
XF:28ID1-ES{LINKAM:T96}:WATER_PUMP_STATUS
XF:28ID1-ES{LINKAM:T96}:WATER_PUMP_TEMP
XF:28ID1-ES{LINKAM:T96}:WATER_PUMP_VOLTAGE

'''

file_loading_timer.stop()