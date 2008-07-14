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
		raise "Usage Error: CoordinateTracker must be subclassed to use process"	

class SingleIRRawCoordinates( CoordinateTracker ):
	##this class will just return the coordinate data form the wiimote
	## without any error correction, 1023s and all. (1023 is what the 
	## wiimote sends if it can't see any IR dots
	def process(self, xys1, xys2 ):
		self.x1,self.y1 = xys1[0][0],xys1[0][1]
		self.dx,self.dy = xys2[0][0]-self.x1,xys2[0][1]-self.y1
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

		

class DoubleCoordinateTracker( CoordinateTracker ):	

	#graph = Dots()
	tracker = SingleCoordinateTracker()
	getCoordinates = tracker.getCoordinates
	
	switch = False
	visible = 15
	def process(self, xys1,xys2 ):
	
		x1,x2,= xys1[0][0],xys1[1][0] ## the first x coordinate from each remote
		x3,x4 = xys2[0][0],xys2[1][0] ## the second x coordinate from each remote
		y1,y2,= xys1[0][1],xys1[1][1] ## the first y coordinate from each remote
		y3,y4 = xys2[0][1],xys2[1][1] ## the second y coordinate from each remote
		
		if not 1023 in (x1,x3):
			p1 = (x1+x3)/2,(y1+y3)/2
		else: p1 = 1023,1023
		if not 1023 in (x2,x4):
			p2 = (x2+x4)/2,(y1+y3)/2
		else: p2 = 1023,1023
			
		self.tracker.process([p1],[p2])
		
	


def CoordinateTrackerFactory(n,correctErrors = False):
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
		
