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



## IR data parser
import time,math

class IRparser:
	
	def __init__(self):
		## nothing interesting here: just setting stuff to zero.
		self.cycles=0 ## Keeps track of how many times data as been parsed
		self.x=0
		self.y=0
		self.z=0
		self.axis=[1,0,0]


	def __get_xy(self, data):
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
		
	def parse(self,dataList):
		## the public method for the parser. Takes a list of wiimote IR data
		## and uses up to the first two. What to do with more than 2 data is 
		## undefined so they are just ignored. 
		if len(dataList) == 0 : 
			return None,None
		if len(dataList) == 1:
			return self.__parseSingle(dataList[0])
		return self.__parseDouble(dataList[0],dataList[1])
			
			
		
	
	def  __parseSingle(self,data):
		if len(data) == 19:
		## the length of the full IR packet is 19. This is the only thing we're interested in. 
			##data[7:10] contains the data for the first set of points
			##data[10:13] contains the second. 
			x,y=self.__get_xy(data[7:10]) 
			## the default datum is 1023; this is what is sent if no dots are visible to the wiimote
			if x!=1023: self.x = x 
			if y!=1023: self.y = y
			
			x,y=self.__get_xy(data[10:13])
			if x!=1023: self.axis[0] = self.x - x
			if y!=1023: self.axis[1] = y - self.y
			
			## if we assume that a line between the two points stays parallell,
			## we can use the distance between them as a metric for z
			## This is pretty arbitrary right now. 
			
			self.z = 500- math.sqrt((self.axis[0])**2 + (self.axis[1])**2 )
			
			return (self.x,self.y,self.z),self.axis
		return None,None
			
			
			
	def __parseDouble(self,data1,data2):
		if len(data1)==19==len(data2):
			## x data comes form wm1, z from wm2
			## both sets of data should have more or less the same vertical height,
			## assuming equal distance from the wiimotes
			
			## Currently this is a very crude approximation of the position of the dots
			## It assumes remotes are at 90 degrees, equal height and that 
			## the wii remotes field of view is linear not radial. 
			
			
			## z11,z12 is undefined

			x11,y11=self.__get_xy(data1[7:10])
			if x11 != 1023: self.x = x11
			if y11 != 1023: self.y = y11
			
			
			
			x12,y12=self.__get_xy(data1[10:13])
			if x12 != 1023: self.axis[0] = self.x - x12
			if y12 != 1023: self.axis[1] = y12 - self.y
			
			
			## x21,x22 is undefined
			z21,y21=self.__get_xy(data2[7:10])
			z22,y22=self.__get_xy(data2[10:13])
			if z21 != 1023: self.z = z21
			if z22 != 1023: self.axis[2] = z22 - self.z
			 
			#print (self.y11-self.y12)-(self.y21-self.y22) ## this should be near 0. It generally isn't
			
			return (self.x,self.y,self.z),(self.axis[0],self.axis[1],self.axis[2])
		return (None,None)
	
			
	