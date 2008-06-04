## This module is designed to test the connection to the wiimote. 
## Button data is very reliable, so 

class ButtonParser:

	def __init__(self):
		self.A = 0

	def parse(self,data):
		if data == None: return None,None
		##on every channel, bytes 2 & 3 are button bytes. 
		##we're actually going to look at just the A button
		
		A = ord(data[0][3]) & 0x08
		if A and not self.A: print "Button A pressed."
		if not A and self.A: print "Button A released."
		self.A = A	
		return None,None
		

		
import sys,time
sys.path.append('.')

from final.WiimoteTalkers import *

address = '00:19:FD:ED:E1:25'  ## address of my wiimote
address2 = '00:19:FD:D7:63:B1' ## address of my second wiimote
talker  = Talker(address2)## Only use a single talker here! 
talker.parser = ButtonParser() ## Replace the IR parser with the button one. 
talker.connect() ##Connect to the wiimote
while 1: talker.refresh();time.sleep(0.01)

