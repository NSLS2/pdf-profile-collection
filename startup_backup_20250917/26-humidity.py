#Voltage output 1
#PV: XF:28ID1-ES{IO-E1241:1}AO:2-SP
#MOXA (E1241) channel: AO1
#Voltage output 2
#PV: XF:28ID1-ES{IO-E1241:1}AO:4-SP
#MOXA (E1241) channel: AO 3
#Voltage input
#PV: XF:28ID1-ES{IO-E1240:1}AI:2-I
#MOXA (E1240) channel: AI 

flow_dry_v = EpicsSignal("XF:28ID1-ES{IO-E1241:1}AO:4-SP",name="flow_dry_v")
flow_wet_v = EpicsSignal("XF:28ID1-ES{IO-E1241:1}AO:2-SP",name="flow_wet_v")
humidity_v = EpicsSignal("XF:28ID1-ES{IO-E1240:1}AI:8-I",name="humidity_v")

def readRH( temperature=25.0, voltage_supply=5.0, coeff_slope=0.030, coeff_offset=0.787, verbosity=3):
        voltage_out = humidity_v.get()
        corr_voltage_out = voltage_out * (5.0 / voltage_supply)
        #For sensor #220 used for SVA chamber
        #coeff_offset = 0.788 #from the certificate
        #coeff_offset = 0.746 #from the environment of RH=0
        #coeff_slope = 0.029
        #For sensor used for Linkam tensile stage
        #coeff_offset = 0.787
        #coeff_slope = 0.030
        #For sensor 114 used for environmental bar
        #coeff_offset = 0.787
        #coeff_slope = 0.030
        #For sensor 43 used in humidity stage
        coeff_offset = 0.816887
        coeff_slope = 0.028813
        sensor_RH = (corr_voltage_out - coeff_offset) / coeff_slope
        true_RH = sensor_RH / (1.0546 - 0.00216 * temperature)      # T in [degC]
        if verbosity >= 3:
                print('Raw sensor RH = {:.3f} pct.'.format(sensor_RH))
                print('T-corrected RH = {:.3f} pct at {:.3f} degC.'.format(true_RH, temperature))
        return true_RH

def flow(dry,wet):
        yield from mov(flow_dry_v,dry)
        yield from mov(flow_wet_v,wet)
 
 
