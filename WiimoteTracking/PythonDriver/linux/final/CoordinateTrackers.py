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
from math import sin,cos,tan,atan,pi,sqrt
def cross(v1,v2):
	return v1[0]*v2[0] + v1[1]*v2[1]

class CoordinateTracker:
	radiansPerPixel = (pi / 4) / 1024.0
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

	
		
	def process(*args):
		raise Error("Usage Error: CoordinateTracker must be subclassed to use process")

class SingleIRRawCoordinates( CoordinateTracker ):
	##this class will just return the coordinate data form the wiimote
	## without any error correction, 1023s and all. (1023 is what the 
	## wiimote sends if it can't see any IR dots
	def process(self, xys1, xys2 ):
		self.x1,self.y1 = xys1[0][0],xys1[0][1]
		self.dx,self.dy = xys2[0][0]-self.x1,xys2[0][1]-self.y1
		## self.z1,z2 = 0 always. 
			
			
class SingleCoordinateTracker( CoordinateTracker ):	

	distBetweenDots = 150
	def __init__(self):
		self.tilt = 0
		self.yaw =  0
		self.thetaX = 0
		self.thetaY = 0
		self.z = 0
	def length(self):
		return self.distBetweenDots	
		
	def getMidpointinCartesian(self):
		cx,sx = cos(self.thetaX), sin(self.thetaX)
		cy,sy = cos(self.thetaY), sin(self.thetaY)
		z = self.z
		return z*sx*cy, z*cx*sy, z*cx*cy
		
		
	def getYaw(self):
		 return self.yaw
	def getTilt(self):
		return self.tilt
		
	def getHorizontalAngleToMidpoint(self):
		return self.thetaX
	
	def getVertiacalAngleToMidpoint(self):
		return self.thetaY
	
	def getDistanceToMidpoint(self):
		return self.z
		
	def getListOfCartesianCoordinates(self):
		cx,sx = cos(self.thetaX), sin(self.thetaX)
		cy,sy = cos(self.thetaY), sin(self.thetaY)
		z = self.z
		midX,midY,midZ = z*sx*cy, z*cx*sy, z*cx*cy
		l = self.distBetweenDots/2
		dx = l*cos(self.tilt)*cos(self.yaw)
		dy = l*sin(self.tilt)
		dz = l*cos(self.tilt)*sin(self.yaw)
		
		return (midX + dx, midY + dy, midZ + dz),(midX - dx, midY - dy, midZ - dz)
		
	def  process(self, xys1,xys2 ):
		x1,y1,x2,y2 = xys1[0][0],xys1[0][1],xys2[0][0],xys2[0][1]

		if 1023 in(x1,x2):
			return
		
		dx = (x2-x1)*self.radiansPerPixel
		dy = (y2-y1)*self.radiansPerPixel
		tanX = tan(dx)
		tanY = tan(dy)
		
		if dx == 0 and dy == 0: return
		z = self.distBetweenDots/2/sqrt(tanX * tanX + tanY * tanY)
		self.z = z
		self.thetaX = (1024 -x1-x2)*self.radiansPerPixel/2
		self.thetaY = (768 - y1-y2)*self.radiansPerPixel/2

		self.yaw = self.thetaX
		if dx != 0:	self.tilt = atan(dy/dx) 
		

class DoubleCoordinateTracker( CoordinateTracker ):	
	old =0,0
	oldVectors = (0,0),(0,0)
	distanceBetweenWiimotes = 37
	switch = 0
	visible = 15
	def length(self):
		return math.sqrt((self.x1-self.x2)**2+(self.y1-self.y2)**2+(self.z1-self.z2)**2)
	
	def getListOfCartesianCoordinates(self):
		return (self.x1,self.y1,self.z1), (
				self.x1 + self.dx,
				self.y1 + self.dy,
				self.z1 + self.dz)
	def getMidpoint(self):
		return (self.x1+self.x2)/2, (self.y1+self.y2)/2,(self.z1+self.z2)/2

	def getAngleFromCenter(self):
		s = sqrt(self.dx**2 + self.dy**2)
		if s == 0: 
			if z>0:return pi/2
			return pi/2
		return math.atan(self.dz/s)
	
	def convertTo3d(self,xA,xB,yA,yB):
			"""See documentation for an explanation of the maths here"""
			thetaAx = (xA-512)*self.radiansPerPixel
			thetaBx = (xB-512)*self.radiansPerPixel
			thetaAy = (yA-384)*self.radiansPerPixel
			thetaBy = (yB-384)*self.radiansPerPixel
					
			t = tan(thetaAx) - tan(thetaBx) 
			if t!= 0:
				z = self.distanceBetweenWiimotes / t
				x = z * tan(thetaAx) - self.distanceBetweenWiimotes/2
				y = z * (tan(thetaAy) + tan(thetaBy)) /2
				return x,y,z
			return 0,0,0
	
	def process(self, xys1,xys2 ):
	
		xA1,xB1,= xys1[0][0],xys1[1][0] ## the first x coordinate from each remote
		xA2,xB2 = xys2[0][0],xys2[1][0] ## the second x coordinate from each remote
		yA1,yB1,= xys1[0][1],xys1[1][1] ## the first y coordinate from each remote
		yA2,yB2 = xys2[0][1],xys2[1][1] ## the second y coordinate from each remote

		## update tells us if we have enough info to update the coordinates
		update  = True
		## visible is a bitmask of the points that are visible
		visible = reduce((lambda x,y: (x << 1) + (y!=1023)),(xA1,xB1,xA2,xB2),0)
		if visible == 15: self.visible = 15 ## we can see everythong
		else: self.visible &=visible ## take away the points we can't see
		update &= self.visible not in (0,1,2,4,8) ##If we've lost sight of three
		## or more dots, then we don't want to update until we see then all again
		

		
		if 1023 not in (xA1,xB1,xA2,xB2):
			## this is a way of telling if we have the two dots mixed
			## up from one remote. It uses the dot product to tell if 
			## the vectors  (xA1,yA1)->(xA2,yA2) and (xB1,yB1)->(xB2,yB2) 
			## point in the same direction			
			v1,v2 = ((xA2-xA1),(yA2-yA1)), ((xB2-xB1),(yB2-yB1))
			v3,v4 = self.oldVectors
			if cross(v1,v2) < 0:
				## The cross product of two vectors in R2 is negative
				## iff the angle between them is greater than pi/2
				## or less than -pi/2
				if   cross(v1,v3) <= 0 and cross(v2,v4) >=0:
					self.switch = 1
					self.oldVectors = (-v1[0],-v1[1]),v2
				elif cross(v1,v3) >= 0 and cross(v2,v4) <=0:
					## This almost never happens. 
					self.switch = 2
					self.oldVectors = v1,(-v2[0],-v2[1])
				else: 
					## Somethings gone a bit wrong. 
					self.update = 0
			else: 
				self.switch = 0
				if cross(v1,v3) <= 0 and cross(v2,v4) <=0:
					if self.switch != 0: self.switch =  3
					self.oldVectors = (-v1[0],-v1[1]),(-v2[0],-v2[1])
				else:
					self.oldVectors = v1,v2
	
		else: update = 0
		if   self.switch == 1:
				xA1,xA2,yA1,yA2 = xA2,xA1,yA2,yA1
		elif self.switch == 2:
				xB1,xB2,yB1,yB2 = xB2,xB1,yB2,yB1
		elif self.switch == 3:
				xA1,xA2,yA1,yA2 = xA2,xA1,yA2,yA1
				xB1,xB2,yB1,yB2 = xB2,xB1,yB2,yB1
				self.switch = 0

		
		## if we've lost sight of one led totaly, then don't update
		#update &= (1023,1023) not in [(xA1,xB1),(xA2,xB2)]
		#update &= (xA1 != 1023  and xB1 != 1023) or (xA2 != 1023 and xB2 != 1023)
		
				
		if update and 1023 not in (xA1,xB1):
			self.x1,self.y1,self.z1 = self.convertTo3d(xA1,xB1,yA1,yB1)
		if update and 1023 not in (xA2,xB2):
			self.x2,self.y2,self.z2 = self.convertTo3d(xA2,xB2,yA2,yB2)
			
		self.dx = self.x2 - self.x1
		self.dy = self.y2 - self.y1
		self.dz = self.z2 - self.z1

def CoordinateTrackerFactory(n,raw = False):
	if n <= 0: 
		print "Cannot parse data of zero length!"
		return SingleIRRawCoordinates()
	if n == 1: 
		if raw:
			return SingleIRRawCoordinates()
		else:
			return SingleCoordinateTracker()
	if n == 2: 
		return DoubleCoordinateTracker()
	if n > 2:
		##Umm....
		return DoubleCoordinateTracker()
		
