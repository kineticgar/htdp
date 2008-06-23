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



## Co-ordinate tracker:
## -SingleCoordinateTracker should be used for a single wiimote
## -DoubleCoordinateTracker shold be used for two or more
## -Both do some error correction to give sensible results.
## -CoordinateTrackercontains common code for single and double
##  which both inherit from CoordinateTracker
##  If your unsure how many wiimotes you will have at run time , use 
##  CoordinateTrackerFactory. This is a factory method that  will return
##  a SingleCoordinateTracker or DoubleCoordinateTracker depending on its argument n. 
## -SingleIRRawCoordinates justreturns the parsed data from the wiimote 
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
	distanceBetweenIRLEDsInmm = 160	
	def correctErrors(self,var1, var2, old1, old2, d):
		if var1  == 1023 and var2 == 1023: 
					return old1,old2,d
		elif var2 == 1023:
			## One dot has gone off-screen so they may have switched.
			## We need to make sure they don't 'jump' by looking at the 
			## difference between the new alue and both old ones. We'll
			## assign the position of the dot to the closer of the two old ones
			if abs(var1 - old1) < abs(var1 - old2):	
					return var1, var1 + d, d
			else: 	return var1 - d, var1, d
			
		elif var1 == 1023: 
			## Same a above but for dot 1
			if abs(var2 - old2) < abs(var2 - old1):
					return var2 - d, var2, d
			else: 	return var2 , var2  + d , d
			
		else:
			#both dots are visible, so  just use them. 
					return var1, var2, var2 - var1
	def  process(self, xys1,xys2 ):
		
		## Check its being used as a single parser...
		assert len(xys1) == 1 == len(xys2)
		## right we only have data frm one wiimote to work with. That means x and
		## y data from this remote can be returned directly for both ir points, and 
		## if we assume that a line between the two points stays perpendicular to the 
		## wiimote, we can use the length of this line as a metric for z
		## This metric is pretty arbitrary right now.
		
		x1,y1,x2,y2 = xys1[0][0],xys1[0][1],xys2[0][0],xys2[0][1]
		## the default datum is 1023; this is what is sent if no dots are visible to the wiimote.
		## If one dot goes off-screen, then we use the visible dot and the last known difference 
		## between them. 
		## x1 = 1023 <=> y1 = 1023 and similarly with x2,y2
		self.x1, self.x2, self.dx = self.correctErrors(x1, x2, self.x1, self.x2, self.dx)
		self.y1, self.y2, self.dy = self.correctErrors(y1, y2, self.y1, self.y2, self.dy)
		
		## if both points are visible and are at more or less the same height,
		## we can use thier distance apart to calculate thier depth. 
		## The following code is not easy to explain in comments, you probably need
		## to sit down with a pencil and some paper to understand it.
		
		if not 1023 in (x1,x2) and abs(y1-y2)<100:
			anglePerPixel = 0.0007677 ## pi/(4*1024)
			## the wiimote has a horizontal field of view of pi/4 (45 degrees) spread 
			## over 1024 pixels.
			## the pi/8 come from the fact that a pixel reading of 0 indicates an angle of 
			## pi/8 off center. 
			
			theta1 = anglePerPixel * min(self.x1,self.x2)
			theta2 = anglePerPixel * max(self.x1,self.x2)
			k = sin(theta2 - theta1)
			if k>0.005: ## div by zero...
				## by changing distance..mm you can callibrate the tracker.
				## z will be the distance from the wiimote in mm. 
				z = self.distanceBetweenIRLEDsInmm*cos(theta2-theta1)/k
			else: z = self.z1
			self.z1 = z
			self.z2 = z

class DoubleCoordinateTracker( CoordinateTracker ):	
	distBetweenWiimotes = 190
	scalingForZ = 1024*distBetweenWiimotes/(2*tan(pi/8))
	anglePerPixel = 0.00076774014017345872
	print scalingForZ
	def process(self, xys1,xys2 ):
		assert 1 < len(xys1) == len(xys2)
		## We have data from at least two wiimotes. We'll only look at the first two for now
		
		## Again, it's hard to explain the following code without a diagram.
		## We're assuming that two wiimotes are parallel and the ditance between them is
		## distBetweenWiimotes
		## The larger this value, the more accurate the calculations will be, but the
		## field of view will be smaller. 	
		
		x1,x2,= xys1[0][0],xys1[1][0]
		x3,x4 = xys2[0][0],xys2[1][0]
		y1,y2,= xys1[0][1],xys1[1][1]
		y3,y4 = xys2[0][1],xys2[1][1]
		if not 1023 in (x1,x2):
			a = abs(x1-x2)
			if a != 0:
				self.z1 = self.scalingForZ/a
				self.x1 = self.distBetweenWiimotes*(x1-512)/a
				self.y1 = self.distBetweenWiimotes*(y1-300)/a
		if not 1023 in (x3,x4):
			b = abs(x3-x4)
			if b !=0:
	 			self.z2 = self.scalingForZ/b	
	 			self.x2 = self.distBetweenWiimotes*(x3-512)/b
	 			self.y2 = self.distBetweenWiimotes*(y3-300)/b

def CoordinateTrackerFactory(n,correctErrors = True):
	if n <= 0: 
		raise "Cannot parse data of zero length!"
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
		
