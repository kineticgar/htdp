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
SET_MODE_IR = chr(CMD_SET_REPORT) + chr(RID_MODE) + chr(0) + chr(MODE_ACC_IR)

	

dataset = [
		[ 0x04B00030,8],
		[ 0x04B00006,0x90],
		[ 0x04B00008, 0x41],
		[ 0x04B0001A, 0x40],
		[ 0x04B00033, 3],
		[ 0x04B00030,8]
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
              
	def send(self,cmd, report, *data ):
		for d in join(cmd, report, data ): print ord(d).__hex__()[2:],
		print
		self.sendSocket.send(join(cmd, report, data ))
		    
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
		""" Connects to the wiimote at address and enable IR
			for much more information and clarity, see
			http://wiibrew.org/index.php?title=Wiimote
		"""
		## Port 19 is where the data will be found
		## Port 17 is the one we want to send our data on.
		self.receiveSocket.connect( ( self.address, 19 ) )
		self.sendSocket.connect( ( self.address, 17 ) )

		## So now we're connected!
		## The Data Reporting Mode is set by sending a two-byte command to Report 0x12: 
		self.send(0x52,0x12,0x00,0x33)
		## 0x00 sets non-continuous reporting
		## 0x33 enables data reporting mode to0x33, the one with IR data. 
		
		## The following procedure should be followed to turn on the IR Camera:

  		## 1. Enable IR Camera (Send 0x04 to Output Report 0x13)
  		self.send(0x52,0x13,0x04);time.sleep(0.01)
		## 2. Enable IR Camera 2 (Send 0x04 to Output Report 0x1a)
		self.send(0x52,0x1a,0x04);time.sleep(0.01)
		## 3. Write 0x08 to register 0xb00030
		self. send(0x52,0x16,0x04,0xb0,0x00,0x30, 1, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 );time.sleep(0.01)
		## 4. Write Sensitivity Block 1 to registers at 0xb00000
		self. send(0x52,0x16,0x4, 0xb0, 0x0, 0x6, 1, 0x90, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);time.sleep(0.01)
		self. send(0x52,0x16,0x4, 0xb0, 0x0, 0x8, 1, 0x41, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);time.sleep(0.01)
		## 5. Write Sensitivity Block 2 to registers at 0xb0001a
		self. send(0x52,0x16,0x4, 0xb0, 0x0, 0x1a, 1, 0x40, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);time.sleep(0.01)
		## 6. Write Mode Number to register 0xb00033
		self. send(0x52,0x16,0x4, 0xb0, 0x0, 0x33, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);time.sleep(0.01)
		## 7. Write 0x08 to register 0xb00030 (again) 
		self. send(0x52,0x16,0x4, 0xb0, 0x0, 0x30, 1, 0x08, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);time.sleep(0.01)

		## This turns the 1st led on.
		self.send(0x52,0x11,0x14) 

		## Set up and start the data-receiving thread
		threading.Thread.__init__ (self)
		
		self.start() 
		print "Connected to %s" % self.address
		return 1

			

def join(cmd, report, data ):
	c = chr(cmd) + chr(report)
	for d in data:
		c += chr(d)
	return c




