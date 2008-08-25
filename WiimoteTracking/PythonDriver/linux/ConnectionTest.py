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

from final.Wiimote3dTracking import Wiimote3dTracker

address = '00:19:FD:ED:E1:25'  ## address of my wiimote
address2 = '00:1A:E9:3B:88:F3' ## address of my second wiimote
talker  =  Wiimote3dTracker(address2)## Only use a single talker here! 
talker.parser = ButtonParser() ## Replace the IR parser with the button one. 
talker.connect() ##Connect to the wiimote
talker.start()

