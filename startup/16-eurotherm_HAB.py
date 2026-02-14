from nslsii.temperature_controllers import Eurotherm

## Made by CHL on 2025/09/17
class eurotherm3k(Eurotherm):
    def __init__(self, pv_prefix, **kwargs):
        # self.tolerance = tolerance ## tolerance already defined in Eurotherm as Cpt(Signal)
        super().__init__(pv_prefix, **kwargs)

    # Re-write the readback and setpoint components due to different PVs
    setpoint = Cpt(EpicsSignal, 'SP', kind='normal')
    setpoint_readback = Cpt(EpicsSignalRO, 'SP:RBV', kind='hinted')

    output = Cpt(EpicsSignal, 'O', kind='normal')
    output_readback = Cpt(EpicsSignalRO, 'O:RBV', kind='hinted')

    ramprate = Cpt(EpicsSignal, 'RR', kind='normal')
    ramprate_readback = Cpt(EpicsSignalRO, 'RR:RBV', kind='hinted')

    working = Cpt(EpicsSignalRO, 'WSP:RBV', kind='hinted')
    readback = Cpt(EpicsSignalRO, 'PV:RBV', kind='hinted')
    temperature = Cpt(EpicsSignalRO, 'PV:RBV', kind='hinted')

    manual_mode = Cpt(EpicsSignal, 'MAN:RBV', kind='normal')
    manual_mode_readback = Cpt(EpicsSignalRO, 'MAN:RBV', kind='hinted')

    autotune = Cpt(EpicsSignal, 'AUTOTUNE', kind='normal')
    autotune_readback = Cpt(EpicsSignalRO, 'AUTOTUNE:RBV', kind='hinted')



eurotherm = eurotherm3k('XF:28ID1-ES{ET:05}LOOP1:', name='eurotherm') ## for temp_controller in 94-load.py

eurotherm3504 = eurotherm3k('XF:28ID1-ES{ET:05}LOOP1:', name='eurotherm3504')
hotairblower = eurotherm3k('XF:28ID1-ES:1{Env:05}LOOP1:', name='hotairblower')


sorensen850_manual = EpicsSignal('XF:28ID1-ES{LS336:1-Out:3}Out:Man-RB', write_pv='XF:28ID1-ES{LS336:1-Out:3}Out:Man-SP', name='sorensen850_manual')

'''
eurotherm3504
XF:28ID1-ES{ET:05}DISABLE
XF:28ID1-ES{ET:05}LOOP1:AUTOTUNE
XF:28ID1-ES{ET:05}LOOP1:AUTOTUNE:RBV
XF:28ID1-ES{ET:05}LOOP1:D
XF:28ID1-ES{ET:05}LOOP1:D:RBV
XF:28ID1-ES{ET:05}LOOP1:I
XF:28ID1-ES{ET:05}LOOP1:I:RBV
XF:28ID1-ES{ET:05}LOOP1:LBT
XF:28ID1-ES{ET:05}LOOP1:LBT:RBV
XF:28ID1-ES{ET:05}LOOP1:MAN
XF:28ID1-ES{ET:05}LOOP1:MAN:RBV
XF:28ID1-ES{ET:05}LOOP1:O
XF:28ID1-ES{ET:05}LOOP1:O:RBV
XF:28ID1-ES{ET:05}LOOP1:OUTPHI
XF:28ID1-ES{ET:05}LOOP1:OUTPHI:RBV
XF:28ID1-ES{ET:05}LOOP1:OUTPLO
XF:28ID1-ES{ET:05}LOOP1:OUTPLO:RBV
XF:28ID1-ES{ET:05}LOOP1:P
XF:28ID1-ES{ET:05}LOOP1:P:RBV
XF:28ID1-ES{ET:05}LOOP1:PV:RBV
XF:28ID1-ES{ET:05}LOOP1:RR
XF:28ID1-ES{ET:05}LOOP1:RR:RBV
XF:28ID1-ES{ET:05}LOOP1:SP
XF:28ID1-ES{ET:05}LOOP1:SP:RBV
XF:28ID1-ES{ET:05}LOOP1:WSP:RBV
XF:28ID1-ES{ET:05}LOOP2:AUTOTUNE
XF:28ID1-ES{ET:05}LOOP2:AUTOTUNE:RBV
XF:28ID1-ES{ET:05}LOOP2:D
XF:28ID1-ES{ET:05}LOOP2:D:RBV
XF:28ID1-ES{ET:05}LOOP2:I
XF:28ID1-ES{ET:05}LOOP2:I:RBV
XF:28ID1-ES{ET:05}LOOP2:LBT
XF:28ID1-ES{ET:05}LOOP2:LBT:RBV
XF:28ID1-ES{ET:05}LOOP2:MAN
XF:28ID1-ES{ET:05}LOOP2:MAN:RBV
XF:28ID1-ES{ET:05}LOOP2:O
XF:28ID1-ES{ET:05}LOOP2:O:RBV
XF:28ID1-ES{ET:05}LOOP2:OUTPHI
XF:28ID1-ES{ET:05}LOOP2:OUTPHI:RBV
XF:28ID1-ES{ET:05}LOOP2:OUTPLO
XF:28ID1-ES{ET:05}LOOP2:OUTPLO:RBV
XF:28ID1-ES{ET:05}LOOP2:P
XF:28ID1-ES{ET:05}LOOP2:P:RBV
XF:28ID1-ES{ET:05}LOOP2:PV:RBV
XF:28ID1-ES{ET:05}LOOP2:RR
XF:28ID1-ES{ET:05}LOOP2:RR:RBV
XF:28ID1-ES{ET:05}LOOP2:SP
XF:28ID1-ES{ET:05}LOOP2:SP:RBV
XF:28ID1-ES{ET:05}LOOP2:WSP:RBV
XF:28ID1-ES{ET:05}PROGNUM
XF:28ID1-ES{ET:05}PROGNUM:RBV
XF:28ID1-ES{ET:05}PROGRESET
XF:28ID1-ES{ET:05}PROGRUN
XF:28ID1-ES{ET:05}PROGSTAT:RBV
XF:28ID1-ES{ET:05}RECSEL
XF:28ID1-ES{ET:05}RECSEL:RBV
XF:28ID1-ES{ET:05}RECSTAT:RBV
'''

