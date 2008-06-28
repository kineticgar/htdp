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

	
	def getCoordinates(self):
		return (self.x1,self.y1,self.z1), (self.x2,self.y2,self.z2)
	

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
	distanceBetweenIRLEDsInmm = 152
	scalingForZ = 1024*distanceBetweenIRLEDsInmm/(2*tan(pi/8))
	
	def  process(self, xys1,xys2 ):
		
		## Check its being used as a single parser...
		assert len(xys1) == 1 == len(xys2)
	
		
		x1,y1,x2,y2 = xys1[0][0],xys1[0][1],xys2[0][0],xys2[0][1]
		## the default datum is 1023; this is what is sent if no dots are visible to the wiimote.
		## If one dot goes off-screen, then we use the visible dot and the last known difference 
		## between them. 
		## x1 = 1023 <=> y1 = 1023 and similarly with x2,y2
		
		
		if 1023 in(x1,x2) and self.z1!=0:
			d = self.scalingForZ/self.z1
		else:
			d = math.sqrt((x2-x1)**2+(y2-y1)**2)
		if d !=0:
			self.z1 = self.scalingForZ/d
			self.z2 = self.z1
			
			if x1==1023 and x2 == 1023:
				pass
			elif x2 == 1023:
				self.x1=self.distanceBetweenIRLEDsInmm*(x1-512)/d
				self.y1=self.distanceBetweenIRLEDsInmm*(y1-512)/d#
				self.x2 = self.x1 + self.dx
				self.y2 = self.y1 + self.dy
			elif x1 == 1023:
				self.x2=self.distanceBetweenIRLEDsInmm*(x2-512)/d
				self.y2=self.distanceBetweenIRLEDsInmm*(y2-300)/d
				self.x1 = self.x2 - self.dx
				self.y1 = self.y2 - self.dy
			else:
				self.x1=self.distanceBetweenIRLEDsInmm*(x1-512)/d
				self.y1=self.distanceBetweenIRLEDsInmm*(y1-300)/d
				self.x2=self.distanceBetweenIRLEDsInmm*(x2-512)/d
				self.y2=self.distanceBetweenIRLEDsInmm*(y2-300)/d
				self.dx = self.x2-self.x1
				self.dy = self.y2-self.y1
class DoubleCoordinateTracker( CoordinateTracker ):	
	distBetweenWiimotes = 100
	scalingForZ = 1024*distBetweenWiimotes/(2*tan(pi/8))
	def process(self, xys1,xys2 ):
		assert 1 < len(xys1) == len(xys2)
		## We have data from at least two wiimotes. We'll only look at the first two for now
		
		## Again, it's hard to explain the following code without a diagram.
		## We're assuming that two wiimotes are parallel and the ditance between them is
		## distBetweenWiimotes
		## The larger this value, the more accurate the calculations will be, but the
		## field of view will be smaller. 	
		
		x1,x2,= xys1[0][0],xys1[1][0] ## the first x coordinate from each remote
		x3,x4 = xys2[0][0],xys2[1][0] ## the second x coordinate from each remote
		y1,y2,= xys1[0][1],xys1[1][1] ## the first y coordinate from each remote
		y3,y4 = xys2[0][1],xys2[1][1] ## the second y coordinate from each remote
		## for the moment we won't deal with incomplete data.
		if 1023 in (x1,x2,x3,x4):
			return
		## we need to check thet the first dot from each remote  reffers to the same led. 
		## We'll do this by looking at the dot product of the the vectors defined 
		## by each pair of points.
		if (x3-x1)*(x4-x2)+(y3-y1)*(y4-y2)<0:	 
			x2,x4,y2,y4 = x4,x2,y2,y4
			
		## Now we can do the psudo triangulation. 
		if not 1023 in (x1,x2):
			a = math.sqrt((x2-x1)**2+(y2-y1)**2)
			if a != 0:
				self.z1 = self.scalingForZ/a
				self.x1 = self.distBetweenWiimotes*(x1-512)/a
				self.y1 = self.distBetweenWiimotes*(y1-300)/a
		if not 1023 in (x3,x4):
			b = math.sqrt((x4-x3)**2+(y4-y3)**2)
			if b !=0:
	 			self.z2 = self.scalingForZ/b	
	 			self.x2 = self.distBetweenWiimotes*(x3-512)/b
	 			self.y2 = self.distBetweenWiimotes*(y3-300)/b
	 	self.size = math.sqrt((self.x1-self.x2)**2+(self.y1-self.y2)**2+(self.z1-self.z2)**2)
	 	print self.size
	 	#print 400<self.size<500, x1,x2,x3,x4,y1,y2,y3,y4,self.size

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
		
