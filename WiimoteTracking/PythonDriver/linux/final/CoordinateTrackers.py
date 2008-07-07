## This file is part of the htdp project as part of Google Summer of Code
## Copyright (C) 2008 Chris Nicholls
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


"""
Co-ordinate tracker:
-SingleCoordinateTracker should be used for a single wiimote
-DoubleCoordinateTracker shold be used for two or more
-Both do some error correction to give sensible results.
-CoordinateTrackercontains common code for single and double
 which both inherit from CoordinateTracker
 If your unsure how many wiimotes you will have at run time , use 
 CoordinateTrackerFactory. This is a factory method that  will return
 a SingleCoordinateTracker or DoubleCoordinateTracker depending on its argument n. 
-SingleIRRawCoordinates justreturns the parsed data from the wiimote 

A Co-ordinate tracker should satisfy tthe following interface:

CoordinateTracker:

	getCoordinates() -> coordinatePair
	process([coordinate],[coordinate]) 
	
	where:
		coordinate :: (int,int,int)
		coordinatePair :: (coordinate,coordinate)
	The two lists passed to process should be a list of each wiimotes 
	view of two ir dots (eg, if there is only one wiimte the args might be this:
	process( [ (34,100) ] , [ (560,76) ] )
	This could be updated to support four dots.
	
"""
import time
import math
pi = math.pi
cos = math.cos
sin = math.sin
tan = math.tan
class CoordinateTracker:

	def __init__(self):
		## We use a dictionary to store values
		self.x1  = 0
		self.x2  = 0
		self.dx  = 0
		self.y1  = 0
		self.y2  = 0
		self.dy  = 0
		self.z1  = 0
		self.z2  = 0
		self.dz  = 0
		self.buttonA = 0

	def length(self):
		return math.sqrt((self.x1-self.x2)**2+(self.y1-self.y2)**2+(self.z1-self.z2)**2)
	def getCoordinates(self):
		return (self.x1,self.y1,self.z1), (
				self.x1 + self.dx,
				self.y1 + self.dy,
				self.z1 + self.dz)
		
	def correct(self,v1,v2,old1,old2,dv,factor,shift =0):
			if v1==1023 and v2 == 1023:
				return old1,old2,dv
			elif v2 == 1023:
				return (v1-shift)*factor ,(v1-shift)*factor  + dv, dv
			elif v1 == 1023:
				return (v2-shift)*factor - dv,(v2-shift)*factor ,dv
			else:
				return (v1-shift)*factor , (v2-shift)*factor,  (v2-shift)*factor - (v1-shift)*factor


	def process(*args):
		raise "Usage Error: AbstractIRParser must be subclassed to use process"	

class SingleIRRawCoordinates( CoordinateTracker ):
	##this class will just return the coordinate data form the wiimote
	## without any error correction, 1023s and all. (1023 is what the 
	## wiimote sends if it can't see any IR dots
	def process(self, xys1, xys2 ):
		## Check its being used as a single parser...
		assert len(xys1) == 1 == len(xys2)		
		self.x1,self.y1 = xys1[0][0],xys1[0][1]
		self.x2,self.y2 = xys2[0][0],xys2[0][1]

		## self.z1,z2 = 0 always. 
			
			
class SingleCoordinateTracker( CoordinateTracker ):	
	distanceBetweenIRLEDsInmm = 152.
	scalingForZ = 1024*distanceBetweenIRLEDsInmm/(2*tan(pi/8))
	
	def  process(self, xys1,xys2,factor = None,shiftx = 512,shifty = 384 ):
		
		## Check its being used as a single parser...
		assert len(xys1) == 1 == len(xys2)
		x1,y1,x2,y2 = xys1[0][0],xys1[0][1],xys2[0][0],xys2[0][1]
		## the default datum is 1023; this is what is sent if no dots are visible to the wiimote.
		## If one dot goes off-screen, then we use the visible dot and the last known difference 
		## between them. 
		## x1 = 1023 <=> y1 = 1023 and similarly with x2,y2
		
		if 1023 in(x1,x2) and self.z1!=0:
			d = self.scalingForZ/self.z1
			## if we cant see both points, assume distance is constant. 
		else:
			d = math.sqrt((x2-x1)**2+(y2-y1)**2) ## 
		if d !=0: ## once things get going, this is almost certain to pass, but it will fail initially
			self.z1 = self.scalingForZ/d
			self.z2 = self.z1
			if not factor:factor = self.distanceBetweenIRLEDsInmm/d
			self.x1,self.x2,self.dx = self.correct(x1,x2,self.x1,self.x2,self.dx,factor,shiftx)
			self.y1,self.y2,self.dy = self.correct(y1,y2,self.y1,self.y2,self.dy,factor,shifty)
			
		#print self.size()	
import pygame		
class Dots:
	def __init__(self,n = 10,colour =(0, 0, 0) ):
		
		self.bgcolor = 255, 255, 255
		self.linecolor = colour
		self.screen = pygame.display.set_mode((1000, 800))
		pygame.draw.circle(self.screen, self.linecolor, (10,10), 30)
		self.screen.fill(self.bgcolor)
	 	pygame.display.flip()
	def draw(self,x1,y1,c):
		pygame.draw.circle(self.screen,c,(x1, y1),2)	
		pygame.display.flip()
class DoubleCoordinateTracker( CoordinateTracker ):	
	old =0,0
	#graph = Dots()
	tracker1 = SingleCoordinateTracker()
	tracker2 = SingleCoordinateTracker()
	switch = False
	visible = 15
	def process(self, xys1,xys2 ):
		assert 1 < len(xys1) == len(xys2)

		x1,x2,= xys1[0][0],xys1[1][0] ## the first x coordinate from each remote
		x3,x4 = xys2[0][0],xys2[1][0] ## the second x coordinate from each remote
		y1,y2,= xys1[0][1],xys1[1][1] ## the first y coordinate from each remote
		y3,y4 = xys2[0][1],xys2[1][1] ## the second y coordinate from each remote
		## we need to check thet the first dot from each remote  reffers to the same led. 
		## We'll do this by looking at the dot product of the the vectors defined 
		## by each pair of points.

		visible = reduce((lambda x,y: (x << 1) + (y!=1023)),(x1,x2,x3,x4),0)
		if visible == 15: self.visible = 15
		else: self.visible &=visible
		if 1023 not in (x1,x2,x3,x4):
			if (x3-x1)*(x4-x2)+(y3-y1)*(y4-y2)<0:    
					self.switch = True
										
			else: 
				self.switch = False
		for x in(x1,x2,x3,x4,y1,y2,y3,y4):
			if x ==1023: print '###',
			else: print  '%03i' %x,
			
		if self.switch:
			x2,x4,y2,y4 = x4,x2,y4,y2
			print 's',
		else: print '~',

		
		if not self.visible in (0,1,2,4,8):
			self.tracker1.process([(x1,y1)],[(x2,y2)])	                
			self.tracker2.process([(x3,y3)],[(x4,y4)])
				
			self.x1,self.y1,self.z1 = self.tracker1.getCoordinates()[0]
			self.x2,self.y2,self.z2 = self.tracker2.getCoordinates()[0]
			self.dx = self.x2 - self.x1
			self.dy = self.y2 - self.y1	
			self.dz = self.z2 - self.z1	
		print "%04i" % self.length(),
		if 160< self.length() < 240:
			print '|||'
		else:
			print '<<<'


def CoordinateTrackerFactory(n,correctErrors = True):
	if n <= 0: 
		print "Cannot parse data of zero length!"
		return SingleIRRawCoordinates()
	if n == 1: 
		if correctErrors:
			return SingleCoordinateTracker()
		else:
			return SingleIRRawCoordinates()
	if n == 2: 
		return DoubleCoordinateTracker()
	if n > 2:
		##Umm....
		return DoubleCoordinateTracker()
		
