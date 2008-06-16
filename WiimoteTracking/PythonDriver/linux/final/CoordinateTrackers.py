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

import math

class :

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
		
		self.z1 = 500- math.sqrt(self.dx**2 + self.dy**2 )
		self.z2 = self.z1

class DoubleCoordinateTracker( CoordinateTracker ):	
			
	def process(self, xys1,xys2 ):
		assert 1 < len(xys1) == len(xys2)
		## We have data from at least two wiimotes. We'llonly look at the first two for now
		
		## Currently this is a very crude approximation of the position of the dots
		## It assumes remotes are at 90 degrees, equal height and that 
		## the wii remotes field of view is linear not radial. 

		## For the moment, x & y data comes form wm1 so the code is a direct copy from above.
		## z data comes from the second wiimote.z\
		## both sets of data should have more or less the same vertical height,
		## assuming equal distance from the wiimotes
		
		x1,y1,x2,y2 = xys1[0][0],xys1[0][1],xys2[0][0],xys2[0][1]
		
		self.x1, self.x2, self.dx = self.correctErrors(x1, x2, self.x1, self.x2, self.dx)
		self.y1, self.y2, self.dy = self.correctErrors(y1, y2, self.y1, self.y2, self.dy)
		
		z1,y3,z2,y4	= xys1[1][0],xys1[1][1],xys2[1][0],xys2[1][1]
		# hopefully y3 ~= y1 and y4 ~= y2
		self.z1, self.z2, self.dz = self.correctErrors(z1, z2, self.z1, self.z2, self.dz)

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
		
