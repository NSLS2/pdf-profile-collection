from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd.signal import AttributeSignal
from ophyd.mixins import EpicsSignalPositioner

from ophyd import Component as C
from ophyd import Component as Cpt
from ophyd.device import DeviceStatus
from ophyd import PVPositioner

from nslsii.temperature_controllers import Eurotherm

class CS700TemperatureController(PVPositioner):
    readback = C(EpicsSignalRO, 'T-I')
    setpoint = C(EpicsSignal, 'T-SP')
    done = C(EpicsSignalRO, 'Cmd-Busy')
    stop_signal = C(EpicsSignal, 'Cmd-Cmd')

    def set(self, *args, timeout=None, **kwargs):
        return super().set(*args, timeout=timeout, **kwargs)

    def trigger(self):
        # There is nothing to do. Just report that we are done.
        # Note: This really should not necessary to do --
        # future changes to PVPositioner may obviate this code.
        status = DeviceStatus(self)
        status._finished()
        return status

# To allow for sample temperature equilibration time, increase
# the `settle_time` parameter (units: seconds).
"""
cs700 = CS700TemperatureController('XF:28ID1-ES:1{Env:01}', name='cs700',
                                   settle_time=0)
cs700.done_value = 0
cs700.read_attrs = ['setpoint', 'readback']
cs700.readback.name = 'temperature'
cs700.setpoint.name = 'temperature_setpoint'
"""

# Do not write a new Eurotherm class use the one from nslsii defined above
# eurotherm = Eurotherm('XF:28ID1-ES:1{Env:04}', name='eurotherm')
# eurotherm.timeout.set(1200)
# eurotherm.equilibrium_time.set(10) # commented by MA

class Eurotherm(EpicsSignalPositioner):
	def set(self, *args, **kwargs):
		return super().set(*args, timeout=100000, **kwargs)


eurotherm = Eurotherm('XF:28ID1-ES:1{Env:04}T-I', write_pv='XF:28ID1-ES:1{Env:04}T-SP', tolerance = 1, name='eurotherm')
### Eurotherm3504 and added by GK on May 14, 2025
#eurotherm3504 = Eurotherm('XF:28ID1-ES{ET:05}LOOP1:SP', name='eurotherm3504')
#eurotherm3504_ramprate = Eurotherm('XF:28ID1-ES{ET:05}LOOP1:RR', name='eurotherm3504_ramprate')
#eurotherm3504_temp = Eurotherm('XF:28ID1-ES{ET:05}LOOP1:RBV', name='eurotherm3504_temp')
# eurotherm3504 = Eurotherm('XF:28ID1-ES{ET:05}LOOP1:PV:RBV', write_pv = 'XF:28ID1-ES{ET:05}LOOP1:SP', name='eurotherm3504')
# eurotherm3504_ramprate = Eurotherm('XF:28ID1-ES{ET:05}LOOP1:RR:RBV', write_pv = 'XF:28ID1-ES{ET:05}LOOP1:RR', name='eurotherm3504')

class CryoStream(Device):
    # readback
    T = Cpt(EpicsSignalRO, 'T-I')
    # setpoint
    setpoint = Cpt(EpicsSignal, read_pv="T-RB",
                   write_pv="T-SP",
                   add_prefix=('suffix', 'read_pv', 'write_pv'))
    # heater power level
    heater = Cpt(EpicsSignal, ':HTR1')

    # configuration
    dead_band = Cpt(EpicsSignal, 'T:AtSP-SP', string=True)
    heater_range = Cpt(EpicsSignal, ':HTR1:Range', string=True)
    # don't know what this is?
    #scan = Cpt(EpicsSignal, ':read.SCAN', string=True)
    mode = Cpt(EpicsSignal, ':OUT1:Mode', string=True)
    cntrl = Cpt(EpicsSignal, ':OUT1:Cntrl', string=True)
    # trigger signal
    trig = Cpt(EpicsSignal, ':read.PROC')

    #def trigger(self):
        #self.trig.put(1, wait=True)
        #return DeviceStatus(self, done=True, success=True)

    def __init__(self, *args, read_attrs=None,
                 configuration_attrs=None, **kwargs):
        if read_attrs is None:
            read_attrs = ['T', 'setpoint']
        #if configuration_attrs is None:
            #configuration_attrs = ['heater_range', 'dead_band',
                                   #'mode', 'cntrl']
        super().__init__(*args, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         **kwargs)
        self._target = None
        self._sts = None

    def _sts_mon(self, value, **kwargs):
        if (self._target is None or
                 np.abs(self._target - value) < float(self.dead_band.get())):
            self.T.clear_sub(self._sts_mon)
            #self.scan.put('Passive', wait=True)
            if self._sts is not None:
                self._sts._finished()
                self._sts = None
            self._target = None

    def set(self, val):
        self._target = val
        self.setpoint.put(val)#, wait=True)
        sts = self._sts = DeviceStatus(self)
        #self.scan.put('.2 second')
        self.T.subscribe(self._sts_mon)

        return sts

    def stop(self, *, success=False):
        self.setpoint.put(self.T.get())
        if self._sts is not None:
            self._sts._finished(success=success)
        self._sts = None
        self._target = None
        #self.scan.put('Passive', wait=True)


# TODO: uncomment later once the device is available
cryostream = CryoStream('XF:28ID1-ES:1{Env:01}', name='cryostream')


class CryoStat1(Device):
    # readback
    T = Cpt(EpicsSignalRO, ':IN1')
    # setpoint
    setpoint = Cpt(EpicsSignal, read_pv=":OUT1:SP_RBV",
                   write_pv=":OUT1:SP",
                   add_prefix=('suffix', 'read_pv', 'write_pv'))
    # heater power level
    heater = Cpt(EpicsSignal, ':HTR1')

    # configuration
    dead_band = Cpt(AttributeSignal, attr='_dead_band')
    heater_range = Cpt(EpicsSignal, ':HTR1:Range', string=True)
    scan = Cpt(EpicsSignal, ':read.SCAN', string=True)
    mode = Cpt(EpicsSignal, ':OUT1:Mode', string=True)
    cntrl = Cpt(EpicsSignal, ':OUT1:Cntrl', string=True)
    # trigger signal
    trig = Cpt(EpicsSignal, ':read.PROC')

    def trigger(self):
        self.trig.put(1, wait=True)
        return DeviceStatus(self, done=True, success=True)

    def __init__(self, *args, dead_band, read_attrs=None,
                 configuration_attrs=None, **kwargs):
        if read_attrs is None:
            read_attrs = ['T', 'setpoint']
        if configuration_attrs is None:
            configuration_attrs = ['heater_range', 'dead_band',
                                   'mode', 'cntrl']
        super().__init__(*args, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         **kwargs)
        self._target = None
        self._dead_band = dead_band
        self._sts = None

    def _sts_mon(self, value, **kwargs):
        if (self._target is None or
                 np.abs(self._target - value) < self._dead_band):
            self.T.clear_sub(self._sts_mon)
            self.scan.put('Passive', wait=True)
            if self._sts is not None:
                self._sts._finished()
                self._sts = None
            self._target = None

    def set(self, val):
        self._target = val
        self.setpoint.put(val, wait=True)
        sts = self._sts = DeviceStatus(self)
        self.scan.put('.2 second')
        self.T.subscribe(self._sts_mon)

        return sts

    def stop(self, *, success=False):
        self.setpoint.put(self.T.get())
        if self._sts is not None:
            self._sts._finished(success=success)
        self._sts = None
        self._target = None
        self.scan.put('Passive', wait=True)

class CryoStat2(Device):
    # readback
    T = Cpt(EpicsSignalRO, ':IN2')
    # setpoint
    setpoint = Cpt(EpicsSignal, read_pv=":OUT2:SP_RBV",
                   write_pv=":OUT2:SP",
                   add_prefix=('suffix', 'read_pv', 'write_pv'))
    # heater power level
    heater = Cpt(EpicsSignal, ':HTR2')

    # configuration
    dead_band = Cpt(AttributeSignal, attr='_dead_band')
    heater_range = Cpt(EpicsSignal, ':HTR2:Range', string=True)
    scan = Cpt(EpicsSignal, ':read.SCAN', string=True)
    mode = Cpt(EpicsSignal, ':OUT2:Mode', string=True)
    cntrl = Cpt(EpicsSignal, ':OUT2:Cntrl', string=True)
    # trigger signal
    trig = Cpt(EpicsSignal, ':read.PROC')

    def trigger(self):
        self.trig.put(1, wait=True)
        return DeviceStatus(self, done=True, success=True)

    def __init__(self, *args, dead_band, read_attrs=None,
                 configuration_attrs=None, **kwargs):
        if read_attrs is None:
            read_attrs = ['T', 'setpoint']
        if configuration_attrs is None:
            configuration_attrs = ['heater_range', 'dead_band',
                                   'mode', 'cntrl']
        super().__init__(*args, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         **kwargs)
        self._target = None
        self._dead_band = dead_band
        self._sts = None

    def _sts_mon(self, value, **kwargs):
        if (self._target is None or
                 np.abs(self._target - value) < self._dead_band):
            self.T.clear_sub(self._sts_mon)
            self.scan.put('Passive', wait=True)
            if self._sts is not None:
                self._sts._finished()
                self._sts = None
            self._target = None

    def set(self, val):
        self._target = val
        self.setpoint.put(val, wait=True)
        sts = self._sts = DeviceStatus(self)
        self.scan.put('.2 second')
        self.T.subscribe(self._sts_mon)

        return sts

    def stop(self, *, success=False):
        self.setpoint.put(self.T.get())
        if self._sts is not None:
            self._sts._finished(success=success)
        self._sts = None
        self._target = None
        self.scan.put('Passive', wait=True)

cryostat1 = CryoStat1('XF:28ID1-ES1:LS335:{CryoStat}', name='cryostat1', dead_band=1)
cryostat2 = CryoStat2('XF:28ID1-ES1:LS335:{CryoStat}', name='cryostat2', dead_band=1)

# TODO : PV needs to be fixed for done signal
# (doesn't work on ramp down)
class LinkamFurnace(PVPositioner):
    readback = C(EpicsSignalRO, 'TEMP')
    setpoint = C(EpicsSignal, 'RAMP:LIMIT:SET')
    done = C(EpicsSignalRO, 'STATUS')
    stop_signal = C(EpicsSignal, 'RAMP:CTRL:SET')
    temperature = C(EpicsSignal, "TEMP")
    

    def __init__(self, *args, setpoint_tolerance=1, **kwargs):
        
        # Sets tolerance for skipping `set` calls when already at setpoint.
        self.setpoint_tolerance = setpoint_tolerance
        super().__init__(*args, **kwargs)

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

# To allow for sample temperature equilibration time, increase
# the `settle_time` parameter (units: seconds).
linkam_furnace = LinkamFurnace('XF:28ID1-ES{LINKAM}:', name='linkam_furnace',
                                   settle_time=0)
linkam_furnace.done_value = 3
linkam_furnace.stop_value = 0
linkam_furnace.setpoint.kind = "normal"
linkam_furnace.readback.kind = "normal"
linkam_furnace.readback.name = 'temperature'
linkam_furnace.setpoint.name = 'temperature_setpoint'


#added by Gihan/Hui for Linkam T96 on 02/18/2025
#This is working. Minimum temp is about 25oC.
######useful command for Linkam_T96
#linkam_T96.ramprate.get(), or linkam_T96.ramprate.set(target_ramprate)
#linkam_T96.setpoint.set(target_temp)
#linkam_T96.readback.get()  or linkam_T96.temperature.get()
#linkam_T96.move(target_temp)
####RE(mv(linkam_T96, target_temp)) is "not working" on 2/20/2025

class LinkamFurnace_T96(PVPositioner):
    readback = C(EpicsSignalRO, ':TEMP')
    setpoint = C(EpicsSignal, ':SETPOINT:SET')
    done = C(EpicsSignalRO, ':STATUS')
    stop_signal = C(EpicsSignal, ':STATUS')
    temperature = C(EpicsSignal, ":TEMP")
    ramprate = C(EpicsSignal,":RAMPRATE:SET")
    

    def __init__(self, *args, setpoint_tolerance=1, **kwargs):
        
        # Sets tolerance for skipping `set` calls when already at setpoint.
        self.setpoint_tolerance = setpoint_tolerance
        super().__init__(*args, **kwargs)

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
linkam_T96 = LinkamFurnace_T96('XF:28ID1-ES{LINKAM:T96}',name='linkam_T96',settle_time=0)
linkam_T96.done_value = 22
linkam_T96.stop_value = 22
linkam_T96.readback.kind = "normal"
linkam_T96.readback.name = 'temperature'
linkam_T96.setpoint.name = 'temperature_setpoint'
linkam_T96.ramprate.name = 'ramprate'


## MA
class Magnet(PVPositioner):
    readback = Cpt(EpicsSignalRO, 'IMAG')
    setpoint = Cpt(EpicsSignal, 'SETIPRG')
    done = Cpt(EpicsSignalRO, 'SETI-Done1')

magnet = Magnet('XF:28ID1-ES{LS625:1}:', name='magnet')
magnet.done_value =0
#

#########control voltage on eurotherm directly
eurovolt = EpicsSignal('XF:28ID1-ES:1{Env:04}Out-SP', name='eurovolt')


from collections import deque

from ophyd import (EpicsMotor, PVPositioner, PVPositionerPC,
                           EpicsSignal, EpicsSignalRO, Device)
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FmtCpt
from ophyd import DynamicDeviceComponent as DDC
from ophyd import DeviceStatus, OrderedDict


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

hotairblower=Eurotherm('XF:28ID1-ES:1{Env:05}LOOP1:PV:RBV',
        write_pv='XF:28ID1-ES:1{Env:05}LOOP1:SP',
        tolerance=1,name='hotairblower')

#older hot air blower
#hotairblower=Eurotherm('XF:28ID1-ES:1{Env:03}T-I',
#        write_pv='XF:28ID1-ES:1{Env:03}T-SP',
#        tolerance=1,name='hotairblower')

sorensen850_manual = EpicsSignal('XF:28ID1-ES{LS336:1-Out:3}Out:Man-RB', write_pv='XF:28ID1-ES{LS336:1-Out:3}Out:Man-SP', name='sorensen850_manual')
