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



## IR data parser:
## SingleIRParser should be used for a single wiimote
## DoubleIRParser shold be used for two or more
## AbstractIRParser contains common code for single and double
## which both inherit from AbstractIRParser
## If your unsure how many wiimotes you will have at run time , use 
## IRParserFactory. This is a factory method that  will return
## a SingleIRParser or DoubleIRParser depending on its argument n. 

import math

class AbstractIRParser:
	
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
		
		
	def __getXY(self, data):
		data = list(data)
		## data three bytes of raw input from the remotes
		## it comes in the form xxxxxxxx yyyyyyyy YYXXssss
		## where x,y are the ls bits of the x,y data, X,Y the ms bits 
		## and s is size data 
		## The following converts this into a more useable format
		data[0] = ord(data[0][0])
		data[1] = ord(data[1][0])
		data[2] = ord(data[2][0])
		
		x1 = data[0]
		y1 = data[1]
		
		x2 = (data[2]>>4) & 3
		y2 = data[2]>>6
		
		x= (x2<<8 ) + x1
		y= (y2<<8 ) + y1
		
		# size is disgarded. 4 bits isn't that usefull. 
		return x,y
		
	def parse(self,data):
		for d in data:
			if len(d) != 19: return None,None
		## the public method for the parser. Takes a list of raw wiimote IR data
		## and uses up to the first two. What to do with more than 2 data is 
		## undefined so they are just ignored. 

		##data[7:10] contains the data for the first set of points
		##data[10:13] contains the second. 
		xys1 = [self.__getXY(d[7:10]) for d in data]
		xys2 = [self.__getXY(d[10:13]) for d in data]
		self.process(xys1,xys2)
		return (self.x1,self.y1,self.z1),(self.x2,self.y2,self.z2)
		
	def checkButtonA(self,data):
		if data == None: return False
		##on every channel, bytes 2 & 3 are button bytes. 
		##we're actually going to look at just the A button
		f = lambda e,d: ord(d[3]) & 0x08 or e
		A = reduce(f,data, False)
		t = self.buttonA
		self.buttonA = A
		return A and not t

	def aggregate(self,var1, var2, old1, old2, d):
		
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
		raise "Usage Error: AbstractIRParser must be sublassed to use process"
		
class SingleIRParser(AbstractIRParser):		

	def  process(self,xys1,xys2):
		
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
		self.x1, self.x2, self.dx = self.aggregate(x1, x2, self.x1, self.x2, self.dx)
		self.y1, self.y2, self.dy = self.aggregate(y1, y2, self.y1, self.y2, self.dy)
		
		self.z1 = 500- math.sqrt(self.dx**2 + self.dy**2 )
		self.z2 = self.z1

class DoubleIRParser(AbstractIRParser):	
			
	def process(self, xys1,xys2):
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
		
		self.x1, self.x2, self.dx = self.aggregate(x1, x2, self.x1, self.x2, self.dx)
		self.y1, self.y2, self.dy = self.aggregate(y1, y2, self.y1, self.y2, self.dy)
		
		z1,y3,z2,y4	= xys1[1][0],xys1[1][1],xys2[1][0],xys2[1][1]
		# hopefully y3 ~= y1 and y4 ~= y2
		self.z1, self.z2, self.dz = self.aggregate(z1, z2, self.z1, self.z2, self.dz)

def IRParserFactory(n):
	if n <= 0: 
		raise "Cannot parse data of zero length!"
	if n == 1: 
		return SingleIRParser()
	if n == 2: 
		return DoubleIRParser()
	if n > 2:
		##Umm....
		return DoubleIRParser()
		

