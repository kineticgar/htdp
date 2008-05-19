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
		## nothing interesting here: just setting stuff to zero.
		self.cycles=0 ## Keeps track of how many times data as been parsed
		self.x1  = 0
		self.x2  = 0
		self.y1  = 0
		self.y2  = 0
		self.z1  = 0
		self.z2  = 0

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
		(self.x1,self.y1,self.z1),(self.x2,self.y2,self.z2)= self.process(xys1,xys2)
		return (self.x1,self.y1,self.z1),(self.x2,self.y2,self.z2)
		
		
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
		## When this is the case, we just use the last usefull recorded position, stored in x1,y1 etc
		if x1 == 1023: x1 = self.x1  
		if y1 == 1023: y1 = self.y1 
		if x2 == 1023: x2 = self.x2 
		if y2 == 1023: y2 = self.y2 
		
		z1 = 500- math.sqrt((x1-x2)**2 + ((y1-y2))**2 )
		z2 = z1
		return (x1,y1,z1),(x2,y2,z2)


class DoubleIRParser(AbstractIRParser):	
			
	def process(self, xys1,xys2):
		assert 1 < len(xys1) == len(xys2)
		## We have data from at least two wiimotes. We'llonly look at the first two for now
		
		## Currently this is a very crude approximation of the position of the dots
		## It assumes remotes are at 90 degrees, equal height and that 
		## the wii remotes field of view is linear not radial. 

		## x,y data comes form wm1, z from wm2
		## both sets of data should have more or less the same vertical height,
		## assuming equal distance from the wiimotes
		
		x1,y1,x2,y2 = xys1[0][0],xys1[0][1],xys2[0][0],xys2[0][1]
		## the default datum is 1023; this is what is sent if no dots are visible to the wiimote.
		## When this is the case, we just use the last usefull recorded position, stored in x1,y1 etc
		if x1 == 1023: x1 = self.x1  
		if y1 == 1023: y1 = self.y1 
		if x2 == 1023: x2 = self.x2 
		if y2 == 1023: y2 = self.y2 


		z1,y3,z2,y4	= xys1[1][0],xys1[1][1],xys2[1][0],xys2[1][1]
		# hopefully y3 ~= y1 nd y4 ~= y2
		if z1 == 1023: z1 = self.z1  
		if z2 == 1023: z2 = self.z2 
		
		return (x1,y1,z1),(x2,y2,z2)

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
		
		
			
	
