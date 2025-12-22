import shutil
config_dir = "/nsls2/data/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/"
"Define Beamline Modes"

def change_energy(option=None):   
    file_path = "~/Documents/MA/Look_up_table.xlsx"
    df = pd.read_excel(file_path)
    Ophyd_object_setpoint = []
    
    print("Please select an option:")
    for i in range(len(df.columns)):
        print(i , df.columns[i])
    try:
        option = int(input().strip())
    except ValueError:
        print("Invalid input")
        return
    
    print('\nPlease wait energy change & optics tuneup taking place\n')
    
    for i in range(len(df)):
        if pd.notna(df[df.columns[option]][i]): # If the values are empty pass
            print(f"{df['Ophyd_object'][i]} , {df[df.columns[option]][i]}")
            obj_name = df['Ophyd_object'][i]
            tln, *rest = obj_name.split('.')
            obj = globals()[tln]
            for c in rest:
                obj = getattr(obj, c)
            Ophyd_object_setpoint.append(obj)
            Ophyd_object_setpoint.append(df[df.columns[option]][i])
        
    #print(Ophyd_object_setpoint)
    # yield from mv(*A)
    RE(mv(*Ophyd_object_setpoint))
    print('\nEnergy change & optics tuneup completed. Please check the beamstopper alignment and perform Enegy calibration measurement\n')

def current_energy():
    file_path = "~/Documents/MA/Look_up_table.xlsx"
    df = pd.read_excel(file_path)
    Ophyd_object_setpoint = []
    if (4<sbm.pitch.position<6):
        print('39.1 keV')
    if (33<sbm.pitch.position<36):
        print('74.9 keV')
    if (23<sbm.pitch.position<25):
        print('110.6 keV')
    if (-18<sbm.pitch.position<-15):
        print('98.4 keV')
    if (-32<sbm.pitch.position<-29):
        print('63.8 keV')
    for i in range(len(df)):
        obj_name = df['Ophyd_object'][i]
        tln, *rest = obj_name.split('.')
        obj = globals()[tln]
        for c in rest:
            obj = getattr(obj, c)
        print(df['Ophyd_object'][i], '=',  obj.position)


        

def BDM_plot():
	from mpl_toolkits.mplot3d import Axes3D
	from matplotlib import pylab as pl
	from PIL import Image
	import numpy as np
	import pylab	
	
	img = Image.open('/nsls2/xf28id1/BDM_camera/BDM_ROI_000.tiff').convert('L')
	z   = np.asarray(img)
	mydata = z[375:450:1, 550:850:1]#y and x
	#mydata = z[164:300:1, 200:1000:1]
	fig = pl.figure(facecolor='w')
	ax1 = fig.add_subplot(1,2,1)
	im = ax1.imshow(mydata,interpolation='nearest',cmap=pl.cm.jet)
	ax1.set_title('2D')

	ax2 = fig.add_subplot(1,2,2,projection='3d')
	x,y = np.mgrid[:mydata.shape[0],:mydata.shape[1]]
	ax2.plot_surface(x,y,mydata,cmap=pl.cm.jet,rstride=1,cstride=1,linewidth=0.,antialiased=False)
	ax2.set_title('3D')
	#ax2.set_zlim3d(0,100)
	pl.show()

# ----------turbo() is a Temporary fix until auto turbo mode is implemented in the css layer---------
from epics import caget, caput
turbo_T = 110 # Turbo turning on temperature
def turbo():
    current_T = cryostream.T.get()
    tb = caget("XF:28ID1-ES:1{Env:01}Cmd:Turbo-Cmd")
    if current_T <= turbo_T and tb == 0:
        caput("XF:28ID1-ES:1{Env:01}Cmd:Turbo-Cmd", 1)
        time.sleep(2)
        caput("XF:28ID1-ES:1{Env:01}Cmd-Cmd", 20)
    if current_T >= turbo_T and tb == 1:
        caput("XF:28ID1-ES:1{Env:01}Cmd:Turbo-Cmd", 0)
        time.sleep(2)
        caput("XF:28ID1-ES:1{Env:01}Cmd-Cmd", 20)    

# get direct beamcurrent
#def I0():
#    I0 = caget("SR:OPS-BI{DCCT:1}I:Real-I")

#---------------------------function to display the dark subtracted last image ----------------------------------
from tifffile import imread, imshow, imsave
def lastimage(n):
    hdr=db[-n]
    for doc in hdr.documents(fill=True):
           data1=doc[1].get('data')
           if data1 != None:
               light_img=data1['pe1c_image']


    dark_uid=hdr.start. get('sc_dk_field_uid')  
    dk_hdrs=db(uid=dark_uid)
    for dk_hdr in dk_hdrs:
       for doc in dk_hdr.documents(fill=True):
           dk_data1=doc[1].get('data')
           if dk_data1 != None:
               dk_img=dk_data1['pe1c_image']

    I = light_img - dk_img
    imshow(I, vmax = (I.sum()/(2048*2048)), cmap = 'jet' )
    imsave("/nsls2/data/pdf/legacy/processed/xpdacq_data/MA_01_27_2023/" + "dark_sub_image" + ".tiff", light_img - dk_img)
    imsave("/nsls2/data/pdf/legacy/processed/xpdacq_data/MA_01_27_2023/" + "dark_image" + ".tiff", dk_img)
    imsave("/nsls2/data/pdf/legacy/processed/xpdacq_data/MA_01_27_2023/" + "light_image" + ".tiff", light_img)
    

#---------------------------------HAB T setpoint threshold--------------------------------------------
def HAB_Tset(t, threshold, settle_time):
	caput("XF:28ID1-ES:1{Env:05}LOOP1:SP", t)
	T_now = hotairblower.get()

	while T_now not in range(t-threshold, t+2*threshold):
		T_now = hotairblower.get()
		time.sleep(0.5)
	time.sleep(settle_time)

#---------------------------------Magnet I setpoint threshold--------------------------------------------
def Magnet_Iset(i, settle_time): # rounds up the setpoint to a integer thres
	RE(mv(magnet.setpoint,i)) 
	I_now = magnet.readback.get()

	while np.around(I_now)!=i :
		I_now = magnet.readback.get()
		time.sleep(0.5)
	time.sleep(settle_time)

def Magnet_Iset2(i, thershold_1_D_point,settle_time): 
	RE(mv(magnet.setpoint,i)) 
	I_now = magnet.readback.get()

	while (I_now*10) not in range(np.around((i-thershold_1_D_point)*10,1), np.around((i+thershold_1_D_point)*10,1)):
		I_now = magnet.readback.get()
		time.sleep(0.5)
	time.sleep(settle_time)

def Cryostat_CF(t, settle_time): # rounds up the setpoint to a integer thres
	RE(mv(cryostat1,t)) 
	t_now = caget('XF:28ID1-ES1:LS335:{CryoStat}:IN2')

	while np.around(t_now)!=i :
		t_now = caget('XF:28ID1-ES1:LS335:{CryoStat}:IN2')
		time.sleep(0.5)
	time.sleep(settle_time)

	
#---------------------------------HAB T setpoint threshold--------------------------------------------
def Humidity_set(a, b, threshold, settle_time):
	RE(flow(a,b))
	H = readRH
	H_now = readRH(verbosity=2)

	while H_now not in range(H-threshold, H+2*threshold):
		H_now = readRH(verbosity=2)
		time.sleep(0.5)
	time.sleep(settle_time)

#---------------------------------Reaction cell--------------------------------------------
'''
def HAB_Tset(t, threshold, settle_time):
	caput("Set point PV", t)
	T_now = caget("Readback PV")

	while T_now not in range(t-threshold, t+2*threshold):
		T_now = caget("Readback PV")
		time.sleep(0.5)
	time.sleep(settle_time)
'''
