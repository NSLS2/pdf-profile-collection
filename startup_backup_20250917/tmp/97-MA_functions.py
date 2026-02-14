"Define Beamline Modes"
def high_resolution():
	print("Resetting white beam slits")
	wb_slits.inboard.move(-8.7605)
	wb_slits.outboard.move(-5.0251)
	
	print("Resetting Monochromator")
	sbm.yaw.move(-0.00013)
	sbm.roll.move(0.000)
	sbm.pitch.move(0.07414)
	sbm.bend.move(0.0084)
	sbm.twist.move(0.0084)

	print("Resetting Mirror")
	Mirror_VFM.y_upstream.move(-2.3695)
	Mirror_VFM.y_downstream_inboard.move(-1.5492)
	Mirror_VFM.y_downstream_outboard.move(-1.2505)
	Mirror_VFM.bend_upstream.move(100)
	Mirror_VFM.bend_downstream.move(100)

	print("Resetting BDM Slits")
	bdm_slits.top.move(0.034)
	bdm_slits.bottom.move(-25363.970)
	bdm_slits.inboard.move(400.040)
	bdm_slits.outboard.move(-4100.075)

	print("Resetting OCM Slits")
	ocm_slits.top.move(-2569.894)
	ocm_slits.bottom.move(2460.259)
	ocm_slits.inboard.move(-844.963)
	ocm_slits.outboard.move(454.959)
	OCM_table.upstream_jack.move(4.70035)
	OCM_table.downstream_jack.move(-4.19820)
	OCM_table.X.move(-8.44701)
	print("Ready to go !")

def high_flux():
	print("Resetting white beam slits")
	wb_slits.inboard.move(-6.7605)
	wb_slits.outboard.move(-3.0251)

	print("Resetting Monochromator")
	sbm.yaw.move(-0.00013)
	sbm.roll.move(0.000)
	sbm.pitch.move(-0.02093)
	sbm.bend.move(5000.0104)
	sbm.twist.move(0.0)

	print("Resetting Mirror")
	Mirror_VFM.y_upstream.move(-2.3695)
	Mirror_VFM.y_downstream_inboard.move(-1.5492)
	Mirror_VFM.y_downstream_outboard.move(-1.2505)
	Mirror_VFM.bend_upstream.move(50)
	Mirror_VFM.bend_downstream.move(50)

	print("Resetting BDM Slits")
	bdm_slits.top.move(0.034)
	bdm_slits.bottom.move(-25363.970)
	bdm_slits.inboard.move(999.39974)
	bdm_slits.outboard.move(-3550.022)
     
	print("Resetting OCM Slits and Table")
	ocm_slits.top.move(-2469.894)
	ocm_slits.bottom.move(2585.259)
	ocm_slits.inboard.move(-564.909)
	ocm_slits.outboard.move(554.960)
	OCM_table.upstream_jack.move(4.70035)
	OCM_table.downstream_jack.move(-4.19820)
	OCM_table.X.move(-8.44701)
	print("Ready to go!")


def BDM_plot():
	from mpl_toolkits.mplot3d import Axes3D
	from matplotlib import pylab as pl
	from PIL import Image
	import numpy as np
	import pylab	
	
	img = Image.open('/nsls2/xf28id1/BDM_camera/BDM_ROI_000.tiff').convert('L')
	z   = np.asarray(img)
	mydata = z[500:800:1, 500:800:1]
	#mydata = z[164:300:1, 200:1000:1]
	fig = pl.figure(facecolor='w')
	ax1 = fig.add_subplot(1,2,1)
	im = ax1.imshow(z,interpolation='nearest',cmap=pl.cm.jet)
	ax1.set_title('2D')

	ax2 = fig.add_subplot(1,2,2,projection='3d')
	x,y = np.mgrid[:mydata.shape[0],:mydata.shape[1]]
	ax2.plot_surface(x,y,mydata,cmap=pl.cm.jet,rstride=1,cstride=1,linewidth=0.,antialiased=False)
	ax2.set_title('3D')
	#ax2.set_zlim3d(0,100)
	pl.show()

#def temp()
#	Det_1_Z.move(1674.44155)
#	Grid_X.move(32)
#	Grid_Y.move(41.75)
#	Grid_Z.move(830.39405)

