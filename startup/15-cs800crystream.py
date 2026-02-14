#Hui and Gihan made this for PDF cryostream on Sep. 06, 2023
#it had "write temerature ramp","triger it", write "cool mode" to drop temperature ASAP with highest Gas Flow(10l/min).

from ophyd import Component as C

class CS800TemperatureController(PVPositioner):
    readback = C(EpicsSignalRO, 'T-RB')
    setpoint = C(EpicsSignal, 'T:Ramp-SP')
    done = C(EpicsSignalRO, 'Phs-I', string=True) #0:ramp, 1:cool, 2:flat, 3:hold, 4:end, 5:purge
    #stop_signal = C(EpicsSignal, ':STOP.PROC')
    runmode = C(EpicsSignalRO, 'Mode-Sts', string=True) #0:runup OK,  2:startup OK, 3:run, 5:shutdown Ok
    #trigger signal
    trig = Cpt(EpicsSignal,'Cmd-Cmd')
    coolsetpoint = C(EpicsSignal, 'T:Cool-SP')
    #targettemp = C(EpicsSignalRO, 'T:Target-I')

    ## Add by CHLin om 2025/10/17
    ramprate = C(EpicsSignal, 'T:RampRate-SP', kind='hinted')

    def set(self, *args, timeout=None, **kwargs):
        return super().set(*args, timeout=timeout, **kwargs)

    def trigger(self):
        # There is nothing to do. Just report that we are done.
        # Note: This really should not necessary to do --
        # future changes to PVPositioner may obviate this code.
        self.trig.put(1, wait=True)
        #status = DeviceStatus(self)
        #status._finished()
        return DeviceStatus(self, done = True, success=True)
    
    def moveto(self, position, timeout=None, move_cb=None, **kwargs):
        if self.runmode.get()!='Shutdown OK':
            self.setpoint.set(position, timeout=timeout, **kwargs)
            self.trig.put(11, wait=True)
            #wait 5 second to allow phaseID update after trigger
            time.sleep(10)
            while self.done.get() != 'Hold':
                time.sleep(0.1)
            return DeviceStatus(self,done = True, success=True)
        else:
            raise ValueError('cs800 is shutdown mode, please restart it')

    def coolto(self, position, timeout=None, move_cb=None, **kwargs):
        if self.runmode.get()!='Shutdown OK':
            self.coolsetpoint.set(position, timeout=timeout, **kwargs)
            self.trig.put(14, wait=True)
            #wait 5 second to allow phaseID update after trigger
            time.sleep(10)
            while self.done.get() != 'Hold':
                time.sleep(0.1)
            return DeviceStatus(self,done = True, success=True)
        else:
            raise ValueError('cs800 is shutdown mode, please restart it')
        
    ## Add by CHLin om 2025/10/17
    def set_and_check(self, setpoint, ramprate=360, tolerance=0.5):
        new_temp = setpoint
        T_from_sensor = self.readback
        start_T = T_from_sensor.get()

        def _check_setpoint(new_value, old_value, **kwargs):
            if abs(new_value - T_from_sensor.get()) < tolerance:
                # print(f'Reached setpoint {T_from_sensor.get()}.')
                return True
            return False
        
        print(f'\nSet {self.name} to temperature = {new_temp} K, using ramp rate = {ramprate}\n')
        # yield from bps.mv(self.ramprate, ramprate, temp_controller.setpoint, new_temp)
        self.ramprate.put(ramprate)
        self.setpoint.put(setpoint)

        ## for cs800 (cryostream), it needs to be triggered
        if self.name == 'cs800':
            # yield from bps.mv(temp_controller.trig, 11)
            self.trig.put(11, wait=True)
            #wait 5 second to allow phaseID update after trigger
            tqdm_sleep(7, message='Wait after trigger')
        print('\n')
    
        status = SubscriptionStatus(T_from_sensor, run=True, callback=_check_setpoint)

        status = temperature_pbar(start_T, self.setpoint.get(), T_from_sensor, tolerance, status)
            
        return status


# To allow for sample temperature equilibration time, increase
# the `settle_time` parameter (units: seconds).
cs800 = CS800TemperatureController('XF:28ID1-ES:1{Env:01}', name='cs800',
                                   settle_time=0)
cs800.done_value = 'Hold'
cs800.read_attrs = ['setpoint', 'readback']
cs800.readback.name = 'temperature'
cs800.setpoint.name = 'temperature_setpoint'