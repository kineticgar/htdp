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
from	CoordinateTrackers import CoordinateTrackerFactory
from IRparser import IRparser
import time
class Talker(threading.Thread):
	
	def __init__(self,*addresses):
		## Accepts an arbitrary number of wiimote addresses as an argument
		## Currently, any remotes past the first two are ignored, as the IR
		## parser doesn't know what to do with them. Niether do I actually...
		
		self.adrs=addresses
		if len(self.adrs) ==0 : self.adrs = self.search()
		self.wiimotes= [Wiimote(adr) for adr in self.adrs]
		self.coordinateTracker = CoordinateTrackerFactory(len(self.wiimotes))
		self.irParser = IRparser()
		self.listeners = []
		threading.Thread.__init__ (self)
	def connect(self):
		## Tries to connect to each address and returns true if everything went ok.
		print "Connecting to wiimotes..."
		return 	not False in [ wm.connect() for wm in self.wiimotes]
		
	def search(self):
		from bluetooth import discover_devices,lookup_name
		print "Searching for wiimotes..."
		wiimotes = discover_devices(10)
		## We need to remove any non- wiimotes. it is possible some wiimotes
		## do not pass this check however. 
		print "Found %i devices" % len(wiimotes)
		wiimotes = filter(lambda x: x[:8]=='00:19:FD', wiimotes)	
		#wiimotes = filter(lambda x: lookup_name(x) == 'Nintendo RVL-CNT-01', wiimotes)
		print "Found %i wiimotes" % len(wiimotes)
		return wiimotes
		
	def disconnect(self):
		# Disconnects from all wiimotes.
		self.r = False
		for wm in self. wiimotes: wm.disconnect()
		print "Disconnecting"

	def run(self,pause = 0.01):
		self.r = True
		while self.r: 	
			self.refresh()
			time.sleep(pause)
			
	def refresh(self):
		## refresh retrieves the data from each wiimote, parses them and 
		## sends them to whoever is listening via the refresh method.
		## if any listener returns false, or the a button is pressed on a remote
		## then we disconnect and quit. 
		data  = [wm.getData() for wm in self.wiimotes]
		xys1, xys2 = self.irParser.parseWiiData( data )
		if xys1 and xys2:
			self.coordinateTracker.process( xys1, xys2 )
		pos1,pos2 = self.coordinateTracker.getCoordinates()
		
		if pos1 and pos2: ## IR parser may return None...
			result = True
			for l in self.listeners:
				result &= l.refresh(pos1,pos2)
		## if one of the listeners wants us to exit, or if the A button is pressed
		## on any remote, then exit.
		if not result or self.irParser.checkButtonA(data): 
			self.disconnect()
			import sys
			sys.exit()	

	def register(self, listener):
		## Adds a listener to the talker
		self.listeners += [listener]
	def getNumberOfWiimotes(self):
		return len(self.adrs)
	def getWiimoteAddress(self):
		return self.adrs
		
class Socket:
	## This sends out the refresh data on the specified port
	## usage:
	##talker.register( Socket() )
	##talker.register( Socket( port = 5035) 
	def __init__(self,host = "",port=4440):
		import sys, socket
		self.data = None
		try:
			self.mySocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
			self.mySocket.connect ( ( '', port ) )
			self.refresh = self._refresh
		except socket.error:
			print "Socket.error: 111, Connection Refused"
	def refresh(*args): return True			
	def _refresh(self,(x1,y1,z1),(x2,y2,z2)):
				if (x1,y1,z1,x2,y2,z2)!= self.data:
					self.mySocket.send("x:%i,y:%i,z:%i,X:%i,Y:%i,Z:%i:1\n" % (x1,y1,z1,x2,y2,z2)) ###
					self.data = (x1,y1,z1,x2,y2,z2)
   				return True		

