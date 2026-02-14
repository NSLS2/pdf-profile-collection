

class SampleEnvironment(Device):
    esc_sample_theta = Cpt(EpicsMotor, 'ECS-Ax:Th1}Mtr')
    esc_sample_2_theta = Cpt(EpicsMotor, 'ECS-Ax:2Th1}Mtr')
    analyzer_theta = Cpt(EpicsMotor, 'ECS-Ax:Th2}Mtr')
    analyzer_2_theta = Cpt(EpicsMotor, 'ECS-Ax:2Th2}Mtr')
    y = Cpt(EpicsMotor, 'Spn:Caplr-Ax:Y}Mtr')
    z = Cpt(EpicsMotor, 'Spn:Caplr-Ax:Z}Mtr')
    ry_yaw = Cpt(EpicsMotor, 'Spn:Caplr-Ax:Ry}Mtr')
    rz_roll = Cpt(EpicsMotor, 'Spn:Caplr-Ax:Rz}Mtr')

ECS_sample_environment = SampleEnvironment('XF:28ID1B-ES{', name='ECS_sample_environment')


class Analyzer(Device):
    y = Cpt(EpicsMotor, 'Y}Mtr')
    z = Cpt(EpicsMotor, 'Z}Mtr')
    ry_yaw = Cpt(EpicsMotor, 'Ry}Mtr')
    rz_roll = Cpt(EpicsMotor, 'Rz}Mtr')

analyzer_goniohead = Analyzer('XF:28ID1B-ES{Spn:Anlzr-Ax:', name='analyzer_goniohead')

