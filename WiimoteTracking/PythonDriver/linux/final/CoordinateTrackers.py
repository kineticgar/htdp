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


class ClassToDetectIfTwoPointsSwapPosition:	
	## Does what it says on the tin. 
	## 
	cs  = [0,0,0,0] 
	def check(self,x1,y1,x2,y2):
		x3,y3,x4,y4 = self.cs ## These are the last good  values 
		## so check returns true if it thinks
		##    (x1,y1) ~ (x3,y3) relate to the same point and 
		##    (x2,y2) ~ (x4,y4) relate to the same point.
		if 1023 not in (x1,x2): ## This implies y1,y2 != 1023
			## since all points are visible, we can guess if the points 
			## have switched direction by taking the dot porduct of
			## (x1,y1)->(x2,y2) and (x3,y3)->(x4,y4) 
			## If they point in the same direction (the dot product 
			## is positive) we assume thay have not switched, and if
			## it is negative, we assume they have.
			if (x2-x1)*(x4-x3)+(y2-y1)*(y4-y3)<0:    
				self.cs = [x2,y2,x1,y1]
				return True
			else: 
				self.cs = [x1,y1,x2,y2]
				return False
		elif x1 != 1023:
			## The second point has gone off-screen so we guess that the 
			## first point refers to the closer of the two old ones. 
			if self.dist(x1,y1,x3,y3) < self.dist(x1,y1,x4,y4):
				## Its closer to the old first point, so everything is ok
				## Replace the first value, use the old second one
				self.cs = [x1,y1,x4,y4]
				return False
			else: 
				## It's closer to the second one so update the second
				## point and reuse the first. 
				self.cs = [x3,y3,x1,y1]
				return True
		elif x2 != 1023:
			## Exactly the same as above, but now the second point is
			## visible. 
			if self.dist(x2,y2,x4,y4) < self.dist(x2,y2,x3,y3):
				self.cs = [x3,y3,x2,y2]
				return False
			else: 
				self.cs = [x2,y2,x4,y4]
				return True
		else: 
			## Neither point is visible so we can't tell anything
			return False
		
		
	def dist(self,x1,y1,x2,y2):
		return (x1-x2)**2 + (y1-y2)**2
		

class DoubleCoordinateTracker( CoordinateTracker ):	
	old =0,0
	#graph = Dots()
	tracker1 = SingleCoordinateTracker()
	tracker2 = SingleCoordinateTracker()
	swapper1 = ClassToDetectIfTwoPointsSwapPosition()
	swapper2 = ClassToDetectIfTwoPointsSwapPosition()
	switch = False
	visible = 15
	def process(self, xys1,xys2 ):
	
		x1,x2,= xys1[0][0],xys1[1][0] ## the first x coordinate from each remote
		x3,x4 = xys2[0][0],xys2[1][0] ## the second x coordinate from each remote
		y1,y2,= xys1[0][1],xys1[1][1] ## the first y coordinate from each remote
		y3,y4 = xys2[0][1],xys2[1][1] ## the second y coordinate from each remote
		for x in(x1,x2,x3,x4,y1,y2,y3,y4):
			if x ==1023: print '###',
			else: print  '%03i' %x,
		## update tells us if we have enough info to update the coordinates
		update  = True
		## visible is a bitmask of the points that are visible
		visible = reduce((lambda x,y: (x << 1) + (y!=1023)),(x1,x2,x3,x4),0)
		if visible == 15: self.visible = 15 ## we can see everythong
		else: self.visible &=visible ## take away the points we can't see
		update &= self.visible not in (0,1,2,4,8) ##If we've lost sight of three
		## or more dots, then we don't want to update until we see then all again
		
	
		## we need to check thet the first dot from each remote  refers to the same led. 
		## Luckily, we have a handy class for this. 
		if self.swapper1.check(x1,y1,x3,y3):
			print '#',
			x1,y1,x3,y3 = x3,y3,x1,y1
		else: print '~',
		if self.swapper2.check(x2,y2,x4,y4):
			print '#',
			x2,y2,x4,y4 = x4,y4,x2,y2
		else: print '~',
		
		
		
		if 1023 not in (x1,x2,x3,x4):
			## this is a way of telling if we have the two dots mixed
			## up from one remote. This shouldn't happen because of the 
			## swapper code above, though it may occasionly happen due
			## to rapid movement. It uses the dot product to tell if 
			## the vectors  (x1,y1)->(x3,y3) and (x2,y2)->(x4,y4) 
			## point in the same direction			
			if (x3-x1)*(x4-x2)+(y3-y1)*(y4-y2)<0:    
				## since we can't tell whats gone wrong, we'll have to guess
				## which points switch. We want to keep this going
				print 'S',
				self.switch = True
				x2,x4,y2,y4 = x4,x2,y4,y2
			else: print '-',	
		else: print ' ',
		## if we've lost sight of one led totaly, then don't update
		update &= (1023,1023) not in [(x1,x2),(x3,x4)]
		
		#update &= (x1 != 1023  and x2 != 1023) or (x3 != 1023 and x4 != 1023)
		if update:
			print 'U',
			self.tracker1.process([(x1,y1)],[(x2,y2)])	                
			self.tracker2.process([(x3,y3)],[(x4,y4)])
				
			self.x1,self.y1,self.z1 = self.tracker1.getCoordinates()[0]
			self.x2,self.y2,self.z2 = self.tracker2.getCoordinates()[0]
			self.dx = self.x2 - self.x1
			self.dy = self.y2 - self.y1	
			self.dz = self.z2 - self.z1	
		else: print ' ',
		print int(self.length())



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
		
