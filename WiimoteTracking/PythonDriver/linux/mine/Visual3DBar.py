from visual import *
from math import sqrt

	
class Bar3D:
	def __init__(self,length,radius,colour):
		
		
		
		sphere(pos=(512,-400,0),radius=10)
		sphere(pos=(-512,-400,0),radius=10)
		sphere(pos=(-512,400,0),radius=10)
		sphere(pos=(512,400,0),radius=10)

		scene.autoscale=0
		scene.range=1000
		scene.center=(4,0,0)
		scene.background=(1,1,1)
		scene.foreground=(0,0,0)
		self.p1 = sphere(radius=5)
		self.p2 = sphere(radius=5)
		
	def set_pos(self,(px,py,pz),(ax,ay,az)):
		self.p1.pos=(px,py,pz)
		self.p2.pos=(px+ax,py+ay,pz+az)
		
		
	def refresh(self,(x1,y1,z1),axis):
		self.set_pos((512-x1,y1-512,1.3*z1),axis)
						

