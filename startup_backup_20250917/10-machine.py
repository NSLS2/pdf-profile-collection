ring_current = EpicsSignalRO('SR:OPS-BI{DCCT:1}I:Real-I', name='ring_current')
photodiode = EpicsSignalRO('XF:28ID1B-OP{Det:1-Det:2}Amp:bkgnd', name='photodiode')

