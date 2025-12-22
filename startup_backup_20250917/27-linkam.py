from ophyd.signal import DerivedSignal
#import inflection, textwrap, ansiwrap

class AtSetpoint(DerivedSignal):
    '''A signal that does bit-wise arithmetic on the Linkam's status code'''
    def __init__(self, parent_attr, *, parent=None, **kwargs):
        code_signal = getattr(parent, parent_attr)
        super().__init__(derived_from=code_signal, parent=parent, **kwargs)

    def inverse(self, value):
        if int(value) & 2 == 2:
            return 1
        else:
            return 0

    def forward(self, value):
        return value

    # def describe(self):
    #     desc = super().describe()
    #     desc[self.name]['units'] = 'eV'
    #     return desc

    
class Linkam(PVPositioner):
    '''An ophyd wrapper around the Linkam T96 controller
    '''

    ## following https://blueskyproject.io/ophyd/positioners.html#pvpositioner
    readback = Cpt(EpicsSignalRO, 'TEMP')
    setpoint = Cpt(EpicsSignal, 'SETPOINT:SET')
    status_code = Cpt(EpicsSignal, 'STATUS')
    done = Cpt(AtSetpoint, parent_attr = 'status_code')

    ## all the rest of the Linkam signals
    init = Cpt(EpicsSignal, 'INIT')
    model_array = Cpt(EpicsSignal, 'MODEL')
    serial_array = Cpt(EpicsSignal, 'SERIAL')
    stage_model_array = Cpt(EpicsSignal, 'STAGE:MODEL')
    stage_serial_array = Cpt(EpicsSignal, 'STAGE:SERIAL')
    firm_ver = Cpt(EpicsSignal, 'FIRM:VER')
    hard_ver = Cpt(EpicsSignal, 'HARD:VER')
    ctrllr_err = Cpt(EpicsSignal, 'CTRLLR:ERR')
    config = Cpt(EpicsSignal, 'CONFIG')
    stage_config = Cpt(EpicsSignal, 'STAGE:CONFIG')
    disable = Cpt(EpicsSignal, 'DISABLE')
    dsc = Cpt(EpicsSignal, 'DSC')
    RR_set = Cpt(EpicsSignal, 'RAMPRATE:SET')
    RR = Cpt(EpicsSignal, 'RAMPRATE')
    ramptime = Cpt(EpicsSignal, 'RAMPTIME')
    startheat = Cpt(EpicsSignal, 'STARTHEAT')
    holdtime_set = Cpt(EpicsSignal, 'HOLDTIME:SET')
    holdtime = Cpt(EpicsSignal, 'HOLDTIME')
    power = Cpt(EpicsSignalRO, 'POWER')
    lnp_speed = Cpt(EpicsSignal, 'LNP_SPEED')
    lnp_mode_set = Cpt(EpicsSignal, 'LNP_MODE:SET')
    lnp_speed_set = Cpt(EpicsSignal, 'LNP_SPEED:SET')

            
    def on(self):
        self.startheat.put(1)

    def off(self):
        self.startheat.put(0)
    
    def on_plan(self):
        return(yield from mv(self.startheat, 1))

    def off_plan(self):
        return(yield from mv(self.startheat, 0))

    def arr2word(self, lst):
        word = ''
        for l in lst[:-1]:
            word += chr(l)
        return word
        
    @property
    def serial(self):
        return self.arr2word(self.serial_array.get())

    @property
    def model(self):
        return self.arr2word(self.model_array.get())
    
    @property
    def stage_model(self):
        return self.arr2word(self.stage_model_array.get())
    
    @property
    def stage_serial(self):
        return self.arr2word(self.stage_serial_array.get())

    @property
    def firmware_version(self):
        return self.arr2word(self.firm_ver.get())

    @property
    def hardware_version(self):
        return self.arr2word(self.hard_ver.get())

    def status(self):
        text = f'\nCurrent temperature = {self.readback.get():.1f}, setpoint = {self.setpoint.get():.1f}\n\n'
        code = int(self.status_code.get())
        if code & 1:
            text += error_msg('Error        : yes') + '\n'
        else:
            text += 'Error        : no\n'
        if code & 2:
            text += go_msg('At setpoint  : yes') + '\n'
        else:
            text += 'At setpoint  : no\n'
        if code & 4:
            text += go_msg('Heater       : on') + '\n'
        else:
            text += 'Heater       : off\n'
        if code & 8:
            text += go_msg('Pump         : on') + '\n'
        else:
            text += 'Pump         : off\n'
        if code & 16:
            text += go_msg('Pump Auto    : yes') + '\n'
        else:
            text += 'Pump Auto    : no\n'
            
        boxedtext(f'Linkam {self.model}, stage {self.stage_model}', text, 'brown', width = 45)


def boxedtext(title, text, tint, width=75):
    '''
    Put text in a lovely unicode block element box.  The top
    of the box will contain a title.  The box elements will
    be colored.
    '''
    remainder = width - 2 - len(title)
    ul        = u'\u2554' # u'\u250C'
    ur        = u'\u2557' # u'\u2510'
    ll        = u'\u255A' # u'\u2514'
    lr        = u'\u255D' # u'\u2518'
    bar       = u'\u2550' # u'\u2500'
    strut     = u'\u2551' # u'\u2502'
    template  = '%-' + str(width) + 's'

    print('')
    print(colored(''.join([ul, bar*3, ' ', title, ' ', bar*remainder, ur]), tint))
    for line in text.split('\n'):
        lne = line.rstrip()
        #add = ' '*(width-ansiwrap.ansilen(lne))
        add = ' '*(width-5)
        print(' '.join([colored(strut, tint), lne, add, colored(strut, tint)]))
    print(colored(''.join([ll, bar*(width+3), lr]), tint))


def colored(text, tint='white', attrs=[],do_thing=False):
    '''
    A simple wrapper around IPython's interface to TermColors
    '''

    if not do_thing:
        from IPython.utils.coloransi import TermColors as color
        tint = tint.lower()
        if 'dark' in tint:
            tint = 'Dark' + tint[4:].capitalize()
        elif 'light' in tint:
            tint = 'Light' + tint[5:].capitalize()
        elif 'blink' in tint:
            tint = 'Blink' + tint[5:].capitalize()
        elif 'no' in tint:
            tint = 'Normal'
        else:
            tint = tint.capitalize()
        return '{0}{1}{2}'.format(getattr(color, tint), text, color.Normal)
    else:
        return(text)

linkam = Linkam('XF:28ID1-ES{LINKAM:T96}:', name='linkam', settle_time=0)  
linkam.wait_for_connection()
