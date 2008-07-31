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

import threading
from Wiimote import Wiimote
from CoordinateTrackers import CoordinateTrackerFactory
from IRparser import IRparser
from bluetooth import discover_devices,lookup_name
import time

class Wiimote3dTracker(threading.Thread):
	useNormalisation = False
	def __init__(self,*addresses):
		## Accepts an arbitrary number of wiimote addresses as an argument
		## Currently, any remotes past the first two are ignored, as the IR
		## parser doesn't know what to do with them. Niether do I actually...

		self.adrs=addresses
		if len(self.adrs) ==1 and type(self.adrs[0]) == list:
			self.adrs = self.adrs[0]
		if len(self.adrs) ==0 : self.adrs = Wiimote3dTracker.search()
		
		self.wiimotes= [Wiimote(adr) for adr in self.adrs]
		self.coordinateTracker = CoordinateTrackerFactory(len(self.wiimotes))
		self.irParser = IRparser()
		self.listeners = []
		
		## set up the stuff needed for threading:
		threading.Thread.__init__ (self)
		
	def connect(self, listOfAddresses = None):
		## Tries to connect to each address and returns true if everything went ok.
		## listOfAddresses is an optional list of addresses to connect to
		print "Connecting to wiimotes..."
		if listOfAddresses:
			self.wiimotes= [Wiimote(adr) for adr in listOfAddresses]

		

		return 	not False in [ wm.connect() for wm in self.wiimotes]
		
	def search(self):
		print "Searching for wiimotes..."
		addresses = discover_devices(0)
		
		print "Found %i devices" % len(addresses)
		## We need to remove any non- wiimotes. 
		addresses.sort(reverse = True)
		threads = [WiimoteIdentifier(x) for x in addresses]
		for t in threads: t.run()
		while any([t.isAlive() for t in threads]): ## checks if any threads are still running
			time.sleep(0.1)
		## now we can remove the ones that passed
		wiimotes = []
		for i in range(len(addresses)):
			if threads[i].isWiimote:
				wiimotes += [addresses[i]]
	
		print "Found %i wiimotes" % len(wiimotes)
		return wiimotes
	search = classmethod(search)
		
	def disconnect(self):
		# Disconnects from all wiimotes.
		self._Thread__stop
		for wm in self. wiimotes: wm.disconnect()
		print "Disconnecting"
		

	def run(self,pause = 0.004):
		while 1: 	
			self.refresh()
			time.sleep(pause)
	
	def refresh(self):
		## refresh retrieves the data from each wiimote, parses them and 
		## sends them to whoever is listening via the refresh method.
		## if any listener returns false, or the a button is pressed on a remote
		## then we disconnect and quit. 
		if all([wm.updated for wm in self.wiimotes]):
			data  = [wm.getData() for wm in self.wiimotes]
			xys1, xys2 = self.irParser.parseWiiData( data )
			if xys1 and xys2:
				self.coordinateTracker.process( xys1, xys2 )
			pos1,pos2 = self.coordinateTracker.getCoordinates()
			
			if pos1 and pos2: ## IR parser may return None...
				if self.useNormalisation:
					pos1 = self._normalise(pos1)
					pos2 = self._normalise(pos2)
				result = True
				for l in self.listeners:
					result &= l.refresh(pos1,pos2)
			## if one of the listeners wants us to exit, or if the A button is pressed
			## on any remote, then exit.
			if not result:# or self.irParser.checkButtonA(data): 
				self.disconnect()
				import sys
				sys.exit()	


	def calibrate(self,MAX=(800,600,1024),howLong = 5):
		## Use this to calibrate the output of the coordinate trackers
		## it loops round, recordng the range of values sent by the 
		## coordinateTracker. 
		## So when this is being called, the IR dots should be waved about
		## as much as possible (to the edges of the wiimotes field of view). 
		print "Starting calibration..."
		startTime = time.time()
		minxyzs,maxxyzs = [2*31]*3,[-2**31]*3##+- inf...not nice but it will do. 
		while time.time() -startTime < howLong:
			self.refresh()
			(x1,y1,z1),(x2,y2,z2) = self.coordinateTracker.getCoordinates()
			minxyzs = [min(minxyzs[i],(x1,y1,z1)[i],(x2,y2,z2)[i]) for i in range(3)]
			maxxyzs = [max(maxxyzs[i],(x1,y1,z1)[i],(x2,y2,z2)[i]) for i in range(3)]
		self.useNormalisation = True ## This is used in refresh()
		
		## Check for div b zero errors and calculate the re-scaling
		self.minxyzs,self.maxxyzs = minxyzs,maxxyzs
		if maxxyzs[0]-minxyzs[0] != 0: 
			s0 = MAX[0]/(float(maxxyzs[0]-minxyzs[0]))
		else: s0 = 1
		if maxxyzs[1]-minxyzs[1] != 0: 
			s1 = MAX[1]/(float(maxxyzs[1]-minxyzs[1]))
		else: s1 = 1
		if maxxyzs[2]-minxyzs[2] != 0: 
			s2 = MAX[2]/(float(maxxyzs[2]-minxyzs[2]))
		else: s2 = 1
		## Scalings should be the same in each direction to avoid distortion
		## so lets use the maximum 
		self.scale=max(s0,s1,s2) 
		print "calibration done.",self.scale
		
	def _normalise(self,(x,y,z),returnAsInt= True):
		## scales the cooridinate to inside the limits set by calibrate.
		## Should only be called after calibrate has been called. 
		x -= self.minxyzs[0]
		y -= self.minxyzs[1]
		z -= self.minxyzs[2]
		x *= 0.8*self.scale
		y *= 0.8*self.scale	
		z *= 0.8*self.scale
		if returnAsInt:
			return map(int,[x,y,z])
		return x,y,z
			
			
	def register(self, listener):
		## Adds a listener to the talker
		self.listeners += [listener]
		
	def getNumberOfWiimotes(self):
		return len(self.adrs)
		
	def getWiimoteAddresses(self):
		return self.adrs
		
	def vibrate(self,address,duration = 1):
		"""Vibrates the specified wiimote for 'duration' seconds"""
		if not address in self.adrs: return
		i = self.adrs.index(address)
		self.wiimotes[i].vibrate(duration)
		
class WiimoteIdentifier(threading.Thread):
	def __init__(self,address):
		self.address = address
		self.isWiimote = None
		## set up the stuff needed for threading
		threading.Thread.__init__ (self) 
		
	def run(self):
		print "Runnin thread for addr %s" % self.address
		name = lookup_name(self.address)
		self.isWiimote = ( name == 'Nintendo RVL-CNT-01') 
		print "addr %s --> %s: %s" %(self.address,self.isWiimote,name)
		
	def check(self):
			## Totaly not needed, but makes using this class nicer. 
			self.start()
