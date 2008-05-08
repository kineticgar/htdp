#from wmd.WMManager import WMManager
from Wiimote import Wiimote
from IRparser import IRparser


class Double_Talker:
	
	def __init__(self,address1, address2):
		## Create a manager for them. Handles the Backend for the wiimotes.

		
		self.wm1 = Wiimote( address1 ) # Handles the Wiimote; connects to it, manages wiimote state and mode, parses wiimote reports
		self.wm2 = Wiimote( address2 ) # second wiimote
		self.parser = IRparser()
		self.listeners = []
		
	def connect(self):
		return 	( self.wm1.connect() and self.wm2.connect())
	
	def disconnect(self): 
		self.wm1.disconnect()
		self.wm2.disconnect()
		
	def refresh(self):
		data1 	 = self.wm1.getData() 
		data2	 = self.wm2.getData()
		pos,axis = self.parser.parse_double(data1,data2)
		if pos and axis:
			for l in self.listeners:
				l.refresh(pos,axis)
			
			
	def register(self, listener):
		self.listeners += [listener]
		
class Single_Talker:
	
	def __init__(self,address):

		## Create a manager for them. Handles the Backend for the wiimotes.
		self.wm1 = Wiimote( address ) # Handles the Wiimote; connects to it, manages wiimote state and mode, parses wiimote reports

		
		self.parser = IRparser()
		self.listeners = []
		
	def connect(self):
		print "Searching for wiimotes"
		return self.wm1.connect() 
				
	
	def disconnect(self): 
		self.wm1.disconnect()

		
	def refresh(self):
		data 	 = self.wm1.getData() 
		pos,axis = self.parser.parse_single(data)
		if pos and axis:
			for l in self.listeners:
				l.refresh(pos,axis)
			
			
	def register(self, listener):
		self.listeners += [listener]
		
		
		
		
class Printer:
	def refresh(self,(x,y,z),(dx,dy,dz)):
			print "%i,%i,%i,%i,%i" % (1,x,y,x+dx,y+dy)
				
