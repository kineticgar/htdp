import time	
from BluetoothDevice import BluetoothDevice
FEATURE_ENABLE = 0x04
IR_MODE_EXP = 3
CMD_SET_REPORT = 0x52
RID_WMEM = 0x16
RID_MODE = 0x12
RID_IR_EN = 0x13
RID_IR_EN2 = 0x1A
MODE_ACC_IR = 0x33
SET_MODE_IR = chr(CMD_SET_REPORT) + chr(RID_MODE) + '0' + chr(MODE_ACC_IR)


class Wiimote(BluetoothDevice):
	
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
		self.sendSeq(self.dataset_ian)
		self.sendSeq(self.dataset_marcan)
		self.sendSeq(self.dataset_ian)
		return 1
		
	def join( self, cmd, report, data ):
		c = chr(cmd) + chr(report)
		for d in data:
			c += chr(d)
		return c


	def convert( self,  offset, datum):
		## This converts the hex values to a format the wiimote will
		## be happy with. 
	    of1 = offset >> 24 & 0xFF #extract offset bytes
	    of2 = offset >> 16 & 0xFF
	    of3 = offset >> 8 & 0xFF
	    of4 = offset & 0xFF
	    data = [datum] + [0]*15 # append zeros to pad data to 16 bytes
	    ## format is [OFFSET (BIGENDIAN),SIZE,DATA (16bytes)]
	    return self.join(CMD_SET_REPORT,RID_WMEM,[of1,of2,of3,of4,1]+data)



	
	def sendSeq( self , dataset):
		
			self.send(SET_MODE_IR)
			self.send(self.join(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE]))
			self.send(self.join(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE]))

			for d0,d1 in dataset:
				time.sleep(0.001)
				self.send(self.convert( d0,d1))



