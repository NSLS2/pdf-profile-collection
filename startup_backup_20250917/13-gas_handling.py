from ophyd import Device, Component as Cpt, EpicsSignal, EpicsSignalRO
from ophyd import OrderedDict

class RGA(Device):

    mass1 = Cpt(EpicsSignal, 'Mass:MID1-SP')
    partial_pressure1 = Cpt(EpicsSignalRO, 'P:MID1-I')
    mass2 = Cpt(EpicsSignal, 'Mass:MID2-SP')
    partial_pressure2 = Cpt(EpicsSignalRO, 'P:MID2-I')
    mass3 = Cpt(EpicsSignal, 'Mass:MID3-SP')
    partial_pressure3 = Cpt(EpicsSignalRO, 'P:MID3-I')
    mass4 = Cpt(EpicsSignal, 'Mass:MID4-SP')
    partial_pressure4 = Cpt(EpicsSignalRO, 'P:MID4-I')
    mass5 = Cpt(EpicsSignal, 'Mass:MID5-SP')
    partial_pressure5 = Cpt(EpicsSignalRO, 'P:MID5-I')
    mass6 = Cpt(EpicsSignal, 'Mass:MID6-SP')
    partial_pressure6 = Cpt(EpicsSignalRO, 'P:MID6-I')
    mass7 = Cpt(EpicsSignal, 'Mass:MID7-SP')
    partial_pressure7 = Cpt(EpicsSignalRO, 'P:MID7-I')
    mass8 = Cpt(EpicsSignal, 'Mass:MID8-SP')
    partial_pressure8 = Cpt(EpicsSignalRO, 'P:MID8-I')
    mass9 = Cpt(EpicsSignal, 'Mass:MID9-SP')
    partial_pressure9 = Cpt(EpicsSignalRO, 'P:MID9-I')

rga = RGA('XF:28ID1-ES{RGA:1}', name='rga')
