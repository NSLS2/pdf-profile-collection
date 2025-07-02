import ophyd
from ophyd import (Device, Component as Cpt,
                   EpicsSignal, EpicsSignalRO, EpicsMotor)
from ophyd.device import DeviceStatus
from nslsii.devices import TwoButtonShutter as _TwoButtonShutter
#import nslsii.devices

Det_1_X = EpicsMotor('XF:28ID1B-ES{Det:1-Ax:X}Mtr', name='Det_1_X', labels=['positioners'])
Det_1_Y = EpicsMotor('XF:28ID1B-ES{Det:1-Ax:Y}Mtr', name='Det_1_Y', labels=['positioners'])
Det_1_Z = EpicsMotor('XF:28ID1B-ES{Det:1-Ax:Z}Mtr', name='Det_1_Z', labels=['positioners'])

Det_2_X = EpicsMotor('XF:28ID1B-ES{Det:2-Ax:X}Mtr', name='Det_2_X', labels=['positioners'])
Det_2_Y = EpicsMotor('XF:28ID1B-ES{Det:2-Ax:Y}Mtr', name='Det_2_Y', labels=['positioners'])
Det_2_Z = EpicsMotor('XF:28ID1B-ES{Det:2-Ax:Z}Mtr', name='Det_2_Z', labels=['positioners'])

Grid_X = EpicsMotor('XF:28ID1B-ES{Env:1-Ax:X}Mtr', name='Grid_X', labels=['positioners'])
Grid_Y = EpicsMotor('XF:28ID1B-ES{Env:1-Ax:Y}Mtr', name='Grid_Y', labels=['positioners'])
Grid_Z = EpicsMotor('XF:28ID1B-ES{Env:1-Ax:Z}Mtr', name='Grid_Z', labels=['positioners'])

# Beam stop motors
class BeamStop(Device):
    x = Cpt(EpicsMotor, 'X}Mtr')
    y = Cpt(EpicsMotor, 'Y}Mtr')

BStop1 = BeamStop('XF:28ID1B-ES{BS:1-Ax:', name='BStop1')
BStop2 = BeamStop('XF:28ID1B-ES{BS:2-Ax:', name='BStop2')
Bstop_Tbl = BeamStop('XF:28ID1B-ES{BS:Tbl-Ax:', name='BStop2_Tbl')

# OCM table widget
class OCMTable(Device):
    ocm_y_upstream = Cpt(EpicsMotor, 'YU}Mtr')
    ocm_y_downstream = Cpt(EpicsMotor, 'YD}Mtr')
    ocm_x_table = Cpt(EpicsMotor, 'X}Mtr')

OCM_table = OCMTable('XF:28ID1B-ES{OCM-Ax:', name='OCM_table')

ECS_tel_guide = EpicsMotor('XF:28ID1B-ES{ECS-Ax:X}Mtr', name='ECS_tel_guide')
ECS_laser_Y = EpicsMotor('XF:28ID1B-ES{Lsr:1-Ax:Y}Mtr', name='ECS_laser_Y') # MA May 22, 2025
ECS_reflective_foil_X = EpicsMotor('XF:28ID1B-ES{Foil:1-Ax:X}Mtr', name='ECS_reflective_foil_X') # MA May 22, 2025

class ECS(Device):
    laser_y = Cpt(EpicsMotor, 'Lsr:1-Ax:Y}Mtr')
    reflective_foil_x = Cpt(EpicsMotor, 'Foil:1-Ax:X}Mtr')
    filter_wheel_1_phi = Cpt(EpicsMotor, 'Fltr:Whl1-Ax:Phi}Mtr')
    filter_wheel_2_phi = Cpt(EpicsMotor, 'Fltr:Whl2-Ax:Phi}Mtr')

ECS_laser_foil_filter = ECS('XF:28ID1B-ES{', name='ECS_laser_foil_filter')

class FilterBank(Device):
    flt1 = Cpt(EpicsSignal, '1}Cmd:Opn-Cmd', string=True)
    flt2 = Cpt(EpicsSignal, '2}Cmd:Opn-Cmd', string=True)
    flt3 = Cpt(EpicsSignal, '3}Cmd:Opn-Cmd', string=True)
    flt4 = Cpt(EpicsSignal, '4}Cmd:Opn-Cmd', string=True)


class TwoButtonShutter(_TwoButtonShutter):
    def stop(self):
        ...
    def set(self, value):
        if value == 0:
            return super().set('Close')
            #super().set('Close')
            #status = DeviceStatus(self)
            #return status
        if value == 1:
            return super().set('Open')
        #    super().set('Open')
        #    status = DeviceStatus(self)
        #    return status

    def read(self): #fix for whoever thought it was smart to use 'Not Open' instead of 'Close' - DO
        ret = super().read()
        val = ret['fb_two_button_shutters_flt1_status']['value']
        if val == 'Not Open':
            ret['fb_two_button_shutters_flt1_status']['value'] = 'Close'
        return ret

    # def read(self):
    #    ret = super().read()
    #    # FIX RET
    #    return ret
class FilterBankTwoButtonShutter(Device):
    flt1 = Cpt(TwoButtonShutter, '1}')
    flt2 = Cpt(TwoButtonShutter, '2}')
    flt3 = Cpt(TwoButtonShutter, '3}')
    flt4 = Cpt(TwoButtonShutter, '4}')

fb = FilterBank('XF:28ID1B-OP{Fltr:', name='fb')
fb_two_button_shutters = FilterBankTwoButtonShutter('XF:28ID1B-OP{Fltr:', name='fb_two_button_shutters')
fb2 = fb_two_button_shutters

#trying to make a temporary shutter - DO - 5/18/2022
fs = fb_two_button_shutters.flt4
#if disable this, need to re-enable fs in 15-optics: line 105

# Spinner Goniohead motors, add by HZ
Spinnergo_X = EpicsMotor('XF:28ID1B-ES{Stg:Smpl-Ax:X}Mtr', name='Spinnergo_X', labels=['positioners'])
Spinnergo_Y = EpicsMotor('XF:28ID1B-ES{Stg:Smpl-Ax:Y}Mtr', name='Spinnergo_Y', labels=['positioners'])
#Spinnergo_Z = EpicsMotor('XF:28ID1B-ES{Stg:Smpl-Ax:Z}Mtr', name='Spinnergo_Z', labels=['positioners']) 
Beam_stop_TBL2 = EpicsMotor('XF:28ID1B-ES{Stg:FTIR-Ax:Y}Mtr', name='Beam_stop_TBL2', labels=['positioners'])
# Above two lines were modified by GK and MA on 01/24/2025
Spinnergo_Ry = EpicsMotor('XF:28ID1B-ES{Stg:Smpl-Ax:Ry}Mtr', name='Spinnergo_Ry', labels=['positioners'])

Tomo_spinner = EpicsMotor('XF:28ID1B-ES{Smpl:Chngr-Ax:YRot}Mtr', name='Tomo_spinner', labels=['positiioners'])

# Defined by CHLin on 2025/05/19
Beam_pipe_X = EpicsMotor('XF:28ID1B-ES{Stg:FTIR-Ax:X}Mtr', name='Beam_pipe_X', labels=['positioners'])

#ECS diffractometer Added by MA
ECS_Sam_tth = EpicsMotor('XF:28ID1B-ES{ECS-Ax:2Th1}Mtr', name='ECS_Sam_tth', labels=['positioners'])
ECS_An_tth = EpicsMotor('XF:28ID1B-ES{ECS-Ax:2Th2}Mtr', name='ECS_An_tth', labels=['positioners'])
ECS_An_th = EpicsMotor('XF:28ID1B-ES{ECS-Ax:Th2}Mtr', name='ECS_An_th', labels=['positioners'])

#detector for ECS - DO and MA
ECS_det1 = EpicsSignalRO(  'XF:28IDC-BI:1{IM:1}:C4_1' ,name='ECS_det1')

#45-degree shifting motor on M6-grid, for use with hot air blower / cryostream with angled sample bracket
broadside45_shifter = EpicsMotor('XF:28ID1B-ES{Smpl:Array-Ax:Horiz}Mtr', name='broadside45_shifter') 
Multi_X = EpicsMotor('XF:28ID1B-ES{Smpl:Array-Ax:Horiz}Mtr', name='Multi_X') 

#NOx BOx x/y sample position
noxbox_x = EpicsMotor('XF:28ID1B-ES{NOx-Ax:X}Mtr', name='noxbox_x')
noxbox_y = EpicsMotor('XF:28ID1B-ES{NOx-Ax:Y}Mtr', name='noxbox_y')


#Table stages
OT_stage_1_X = EpicsMotor('XF:28ID1-ES{Det-Ax:X1}Mtr', name='OT_stage_1_X', labels=['positioners'])
OT_stage_1_Y = EpicsMotor('XF:28ID1B-ES{Stg:FTIR-Ax:Y}Mtr', name='OT_stage_1_Y', labels=['positioners'])

OT_stage_2_X = EpicsMotor('XF:28ID1-ES{Det-Ax:X2}Mtr', name='OT_stage_2_X', labels=['positioners'])
OT_stage_2_Y = EpicsMotor('XF:28ID1B-ES:1{Sample:Tbl-Ax:Y1}Mtr', name='OT_stage_2_Y', labels=['positioners'])

OT_stage_3_X = EpicsMotor('XF:28ID1-ES{Det-Ax:X3}Mtr', name='OT_stage_3_X', labels=['positioners'])

OT_stage_4_X = EpicsMotor('XF:28ID1-ES{Det-Ax:X4}Mtr', name='OT_stage_4_X', labels=['positioners'])



#Pin_diode = EpicsMotor('XF:28ID1B-OP{Det:1-Det:2}Amp:bkgnd', name='Pin_diode', labels=['positioners'])  #GK added on Feb12,2025

