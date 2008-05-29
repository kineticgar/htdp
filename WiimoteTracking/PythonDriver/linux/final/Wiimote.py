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
import time	
from bluetooth import set_packet_timeout, BluetoothSocket,L2CAP

FEATURE_ENABLE = 0x04
IR_MODE_EXP = 3
CMD_SET_REPORT = 0x52
RID_WMEM = 0x16
RID_MODE = 0x12
RID_IR_EN = 0x13
RID_IR_EN2 = 0x1A
MODE_ACC_IR = 0x33
SET_MODE_IR = chr(CMD_SET_REPORT) + chr(RID_MODE) + '0' + chr(MODE_ACC_IR)

	
dataset_ian = [
		[ 0x04B00030, 0x01 ],
		[ 0x04B00030, 0x08 ],
		[ 0x04B00006, 0x90 ],## These
		[ 0x04B00008, 0x41 ],## Set
		[ 0x04B0001A, 0x40 ],## Sensitivity
		[ 0x04B00033, 0x33 ],
		[ 0x04B00030, 0x08 ]
	    ]		
dataset_marcan = [
		[ 0x04B00030,8],
		[ 0x04B00006,0x90],
		[ 0x04B00008, 0xC0],
		[ 0x04B0001A, 0x40],
		[ 0x04B00033, 3]
		]	
		
		
class Wiimote(threading.Thread):

	def __init__(self,address):     
		self.address = address
		## Create two bluetooth sockets: 
		##              One to receive data,
		##              One to send config data
		self.receiveSocket = BluetoothSocket( L2CAP )
		self.sendSocket = BluetoothSocket( L2CAP )
		self.data = None
              
	def send(self,data):
		self.sendSocket.send(data)
		    
	def getData(self):
		return self.data
		    
	def disconnect(self):
		self.receiveSocket.close()
		self.sendSocket.close()	
		    
	def run(self):
		## Continually receive data from the wiimote to avoid backlog. 
		while 1:
			self.data =  self.receiveSocket.recv(19)

	def connect(self):
		"Connects to the wiimote at address and enable IR"
		## Port 19 is where the data will be found
		## Port 17 is the one we want to send our data on.
		self.receiveSocket.connect( ( self.address, 19 ) )
		self.sendSocket.connect( ( self.address, 17 ) )

		## So now we're connected!
		## Time to set up the IR
		## Ok: this is a little bit of a walkaround/hack
		## sending this sequnce of data seems to be very
		## reliable though I haven't yet worked out why. 
		self.sendSeq(dataset_ian)
		self.sendSeq(dataset_marcan)
		self.sendSeq(dataset_ian)
		#set_packet_timeout( self.address, 10)

		## For more infomation on the wiimote IR api see:
		##  http://wiibrew.org/index.php?title=Wiimote#Initialization 

		## Set up and start the data-receiving thread
		threading.Thread.__init__ (self)
		self.start() 
		print "Connected to %s" % self.address
		return 1

	def sendSeq( self , dataset):
		self.send(SET_MODE_IR)
		self.send( join(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE]))
		self.send( join(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE]))

		for d0,d1 in dataset:
			time.sleep(0.001)
			self.send( convert( d0,d1))

def join(cmd, report, data ):
	c = chr(cmd) + chr(report)
	for d in data:
		c += chr(d)
	return c

def convert(offset, datum):
	## This converts the hex values to a format the wiimote will
	## be happy with. 
	of1 = offset >> 24 & 0xFF #extract offset bytes
	of2 = offset >> 16 & 0xFF
	of3 = offset >> 8 & 0xFF
	of4 = offset & 0xFF
	data = [datum] + [0]*15 # append zeros to pad data to 16 bytes
	## format is [OFFSET (BIGENDIAN),SIZE,DATA (16bytes)]
	return join(CMD_SET_REPORT,RID_WMEM,[of1,of2,of3,of4,1]+data)


