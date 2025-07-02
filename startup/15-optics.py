"Define motors related to optics"
import time as ttime

from ophyd.status import SubscriptionStatus
from ophyd import Signal
from ophyd.sim import NullStatus


class Slits(Device):
    top = Cpt(EpicsMotor, 'T}Mtr')
    bottom = Cpt(EpicsMotor, 'B}Mtr')
    inboard = Cpt(EpicsMotor, 'I}Mtr')
    outboard = Cpt(EpicsMotor, 'O}Mtr')
    ''' TODO : Add later
    xc = Cpt(EpicsMotor, 'XCtr}Mtr')
    xg = Cpt(EpicsMotor, 'XGap}Mtr')
    yc = Cpt(EpicsMotor, 'YCtr}Mtr')
    yg = Cpt(EpicsMotor, 'YGap}Mtr')
    '''

OCM_slits = Slits('XF:28ID1B-OP{Slt:2-Ax:', name='OCM_slits')  # OCM Slits
BDM_slits = Slits('XF:28ID1A-OP{Slt:1-Ax:', name='BDM_slits')  # BD Slits
#Added by MA 09/03/2019
WB_slits = Slits('XF:28ID1A-OP{Slt:0-Ax:', name='WB_slits')  # WB Slits
#Added by MA 10/21/2024
cleanup_slits = Slits('XF:28ID1B-OP{Slt:AS-Ax:', name='cleanup_slits')  # WB Slits


class SideBounceMono(Device):
    x_wedgemount = Cpt(EpicsMotor, "X}Mtr")
    y_wedgemount = Cpt(EpicsMotor, "Y}Mtr")
    yaw = Cpt(EpicsMotor, "Yaw}Mtr")
    pitch = Cpt(EpicsMotor, "Pitch}Mtr")
    roll = Cpt(EpicsMotor, "Roll}Mtr")
    #bend = Cpt(EpicsMotor, "Bend}Mtr")
    #twist = Cpt(EpicsMotor, "Twist}Mtr")
    # Added below and commented above by MA 10/21/2024
    bend_inboard_U = Cpt(EpicsMotor, "IU}Mtr")
    bend_inboard_L = Cpt(EpicsMotor, "IL}Mtr")
    bend_outboard_U = Cpt(EpicsMotor, "OU}Mtr")
    bend_outboard_L = Cpt(EpicsMotor, "OL}Mtr")

sbm = SideBounceMono("XF:28ID1A-OP{Mono:SBM-Ax:", name='sbm')
#temporary fast shutter
#class tempFSShutter:
#
#    def set(self, value):
#        if value == 0:
#            return fb_two_button_shutters.flt1.set('Close')
#        elif value == 1:
#            return fb_two_button_shutters.flt1.set('Open')
#
#    def read(self):
#        return fb_two_button_shutters.read()
#
#    def describe(self):
#        return fb_two_button_shutters.describe()
#
#    def stop(self, success=False):
#        return self.set('close')
#
#fs = tempFSShutter()

# Close the shutter on stop
# fs.stop = lambda *args, **kwargs: fs.set(0)

class PDFFastShutter(Device):
    cmd = Cpt(EpicsSignal, 'Cmd', kind='omitted')
    status = Cpt(EpicsSignal, 'Sts', kind='omitted')
    settle_time = Cpt(Signal, kind='config', value=.1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.st = None
        # TODO: ask CJ to change it downstream to only accept the 'Open' or 'Close' strings (no numbers please!).
        self.setmap = {'Open': 0, 'Close': 1,
                       1: 0, 0: 1}  # MR: this is an inversed logic on the xpdacq side
        self.readmap = {0: 'Open', 1: 'Close'}

    def set(self, val):
        # NOTE: temporary workaround until the fast shutter works.
        #
        def check_if_done(*, value, old_value, **kwargs):
            print(f"{old_value=}  -> {value=}")
            if ((val in ['Open', 1] and value == 0) or
                (val in ['Close', 0] and value == 1)):
                if self.st is not None:
                    self.st._finished()
                    self.st = None
                return True
            return False
        self.cmd.set(self.setmap[val])
        status = SubscriptionStatus(self.status, check_if_done, settle_time=self.settle_time.get())
        return status

        #ttime.sleep(1.0)  # wait to set the value since the status PV does not capture the actual status
        #return NullStatus()

    def get(self):
        return self.readmap[self.cmd.get()]

    def read(self):
        d = super().read()
        d[self.name] = {'value': self.get(), 'timestamp': time.time()}
        return d

    # def stop(self, success=False):
    #     return self.set('Close')

#temporary disable fast shutter while broken - DO 5/18/2022
# fs = PDFFastShutter('XF:28ID1B-OP{PSh:1-Det:2}', name='fs')
#if enable this, need to disable fs in 12-motors: line 80

class Mirror(Device):
    y_upstream = Cpt(EpicsMotor, 'YU}Mtr')
    y_downstream_inboard = Cpt(EpicsMotor, 'YDI}Mtr')
    y_downstream_outboard = Cpt(EpicsMotor, 'YDO}Mtr')
    bend_upstream = Cpt(EpicsMotor, 'BndU}Mtr')
    bend_encoder = Cpt(EpicsSignalRO, 'BndU}Pos:Enc-I')
    bend_downstream = Cpt(EpicsMotor, 'BndD}Mtr')
    twist_encoder = Cpt(EpicsSignalRO, 'BndD}Pos:Enc-I')
    # TODO: add coordinated motions later:
    # y_upstream, y_downstream_inboard, y_downstream_outboard

Mirror_VFM = Mirror('XF:28ID1A-OP{Mir:VFM-Ax:', name='Mirror_VFM')

class OpticsTableADC(Device):
    upstream_jack_inboard = Cpt(EpicsMotor, 'YUI}Mtr')
    upstream_jack_outboard = Cpt(EpicsMotor, 'YUO}Mtr')
    downstream_jack_outboard = Cpt(EpicsMotor, 'YD}Mtr')
    X_upstream = Cpt(EpicsMotor, 'XU}Mtr')
    X_downstream = Cpt(EpicsMotor, 'XD}Mtr')
    Z = Cpt(EpicsMotor, 'Z}Mtr')

optics_table_adc = OpticsTableADC(prefix="XF:28ID1B-ES{Tbl:1-Ax:",
                                  name="optics_table_adc")

class SpinnerGoniohead(Device):
    X = Cpt(EpicsMotor, 'X}Mtr')
    Y = Cpt(EpicsMotor, 'Y}Mtr')
    Z = Cpt(EpicsMotor, 'Z}Mtr')
    Ry = Cpt(EpicsMotor, 'Ry}Mtr')

spinner_goniohead = SpinnerGoniohead(prefix="XF:28ID1B-ES{Stg:Smpl-Ax:",
                                     name="spinner_goniohead")

# Added by MA - Sept 5, 2019
class OCMTable(Device):
    upstream_jack = Cpt(EpicsMotor, 'YU}Mtr')
    downstream_jack = Cpt(EpicsMotor, 'YD}Mtr')
    X = Cpt(EpicsMotor, 'X}Mtr')
 
OCM_table = OCMTable(prefix="XF:28ID1B-ES{OCM-Ax:",
                                  name="optics_table")
