"Non-wmd file"
from wmd.Common import *
import time	

CMD_SET_REPORT = 0x52
RID_MODE = 0x12
MODE_ACC_IR = 0x33
RID_IR_EN = 0x13
FEATURE_ENABLE = 0x04


FEATURE_DISABLE = 0x00
FEATURE_ENABLE = 0x04

IR_MODE_OFF = 0
IR_MODE_STD = 1
IR_MODE_EXP = 3
IR_MODE_FULL = 5

CMD_SET_REPORT = 0x52

RID_LEDS = 0x11
RID_MODE = 0x12
RID_IR_EN = 0x13
RID_SPK_EN = 0x14
RID_STATUS = 0x15
RID_WMEM = 0x16
RID_RMEM = 0x17
RID_SPK = 0x18
RID_SPK_MUTE = 0x19
RID_IR_EN2 = 0x1A

MODE_BASIC = 0x30
MODE_ACC = 0x31
MODE_ACC_IR = 0x33
MODE_FULL = 0x3e

from BluetoothDevice import BluetoothDevice
class Wiimote(BluetoothDevice):
	
		
		
	def connect(self):
		"Connects to the wiimote at address and enable IR"
		## Port 19 is where the data will be found
		## Port 17 is the one we want to send our data on.
		self.receiveSocket.connect( ( self.address, 19 ) )
   		self.sendSocket.connect( ( self.address, 17 ) )
   		
		assert self.receiveSocket and self.sendSocket
		## So now we're connected!
		## Time to set up the IR
		#SET_MODE_IR = chr(CMD_SET_REPORT) + chr(RID_MODE) + '0' + chr(MODE_ACC_IR)
		#self.send(SET_MODE_IR)
		self.seq_ian()
		self.seq_marcan()
		self.seq_ian()
		return 1
		
	def send( self, cmd, report, data ):
		c = chr(cmd) + chr(report)
		for d in data:
			c += chr(d)
		self.sendSocket.send(c)	


  # size here is redundant, since we can just use len(data) if we want.
	def senddata( self, data, offset, size): # see writing to data: [[#On-board Memory].
	    of1 = offset >> 24 & 0xFF #extract offset bytes
	    of2 = offset >> 16 & 0xFF
	    of3 = offset >> 8 & 0xFF
	    of4 = offset & 0xFF
	    data2 = data + [0]*(16-len(data)) # append zeros to pad data if less than 16 bytes
	    if len(data2) > 16:
	      data2 = data2[:16] # crop data if we have too much
	    # format is [OFFSET (BIGENDIAN),SIZE,DATA (16bytes)]
	    self.send(CMD_SET_REPORT,RID_WMEM,[of1,of2,of3,of4,size]+data2)

	def getData(self):
  		return self.receiveSocket.recv(1024)

		
	def disconnect(self):
		"Disconnects the wiimote"
		self.receiveSocket.close()
		self.sendSocket.close()
	

	
	def seq_ian( self ):
		
			SET_MODE_IR = chr(CMD_SET_REPORT) + chr(RID_MODE) + '0' + chr(MODE_ACC_IR)
			self.sendSocket.send(SET_MODE_IR)#; time.sleep(0.005)
			
			self.send(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE])#; time.sleep(0.003)
			
			self.send(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE])

			dataset = [
				[ 0x04B00030, 0x01 ],
				[ 0x04B00030, 0x08 ],
				[ 0x04B00006, 0x90 ],## These
				[ 0x04B00008, 0x41 ],## Set
				[ 0x04B0001A, 0x40 ],## Sensitivity
				[ 0x04B00033, 0x33 ],
				[ 0x04B00030, 0x08 ]
		    	]	
			for d in dataset:
				time.sleep(0.001)
				self.senddata( [ d[1] ], d[0], 1 )

	def seq_marcan( self ):
	# this seems to be the minimal code to get it to work
		SET_MODE_IR = chr(CMD_SET_REPORT) + chr(RID_MODE) + '0' + chr(MODE_ACC_IR)
		self.sendSocket.send(SET_MODE_IR); time.sleep(0.005)
		self.send(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE])
		self.send(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE])
		self.senddata([8],0x04B00030,1) # enable IR data out
		self.senddata([0x90],0x04B00006,1) # sensitivity constants (guessed, Cliff seems to have more data, but this works for me)
		self.senddata([0xC0],0x04B00008,1)
		self.senddata([0x40],0x04B0001A,1)
		self.senddata([IR_MODE_EXP],0x04B00033,1) # enable IR output with specified data format


