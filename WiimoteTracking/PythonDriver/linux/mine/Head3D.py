from visual import *
from math import sqrt

class Scene:

	
	def __init__(self):
		
		k = 1000
		w=3
		
		cylinder(pos=(k,-k,0),radius=w,  axis = (0,0,-20000))
		cylinder(pos=(-k,-k,0),radius=w,  axis = (0,0,-20000))
		cylinder(pos=(-k,k,0),radius=w, axis = (0,0,-20000))
		cylinder(pos=(k,k,0),radius=w,  axis = (0,0,-20000))
		cylinder(pos=(k,0,0),radius=w,  axis = (0,0,-20000))
		cylinder(pos=(-k,0,0),radius=w,  axis = (0,0,-20000))
		cylinder(pos=(0,-k,0),radius=w, axis = (0,0,-20000))
		cylinder(pos=(0,k,0),radius=w,  axis = (0,0,-20000))
		
		for z in range(0,-30000,-3000):
			cylinder(pos=(k,-k,z),radius=w,  axis = (-2*k,0,0))
			cylinder(pos=(-k,-k,z),radius=w,  axis = (0,2*k,0))
			cylinder(pos=(-k,k,z),radius=w, axis = (2*k,0,0))
			cylinder(pos=(k,k,z),radius=w,  axis = (0,-2*k,0))
		scene.autoscale=0
		scene.range=2*k
		scene.center=(4,0,0)


		self.make((400,0,200))
		self.make((400,0,200))
		self.make((100,100,-200))
		self.make((300,-400,-500))
		
		
		self.scene=scene
		
	def set_pos(self,(px,py,pz),(ax,ay,az)):
		self.p1.pos=(px,py,pz)
		self.p2.pos=(px+ax,py+ay,pz+az)
		
		
	def refresh(self,(x1,y1,z1),axis):
		self.scene.center = (512-x1,y1-512,3*z1)
		
	def make(self,pos):
			s=sphere(radius=20,pos=pos)		
			c	=	cylinder(pos=pos,radius=1,  axis = (0,0,-20000))
