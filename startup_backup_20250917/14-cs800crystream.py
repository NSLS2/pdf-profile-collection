#Hui and Gihan made this for PDF cryostream on Sep. 06, 2023
#it had "write temerature ramp","triger it", write "cool mode" to drop temperature ASAP with highest Gas Flow(10l/min).



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


# To allow for sample temperature equilibration time, increase
# the `settle_time` parameter (units: seconds).
cs800 = CS800TemperatureController('XF:28ID1-ES:1{Env:01}', name='cs800',
                                   settle_time=0)
cs800.done_value = 'Hold'
cs800.read_attrs = ['setpoint', 'readback']
cs800.readback.name = 'temperature'
cs800.setpoint.name = 'temperature_setpoint'