from wmd.EVDispatcher import EVDispatcher
from wmd.WMManager import WMManager
from IRparser import IRparser


class Double_Talker:
	
	def __init__(self,address1, address2):

		## Create a manager for them. Handles the Backend for the wiimotes.
		
		evDis = EVDispatcher()
		
		self.wm1 = WMManager( address1, evDis ) # Handles the Wiimote; connects to it, manages wiimote state and mode, parses wiimote reports
		self.wm2 = WMManager( address2, evDis ) # second wiimote
		self.parser = IRparser()
		self.listeners = []
		
	def connect(self):
		return 	( self.wm1.connect() and self.wm2.connect() 
				  and self.wm1.setup() and self.wm2.setup() 
				)
	
	def disconnect(self): 
		self.wm1.disconnect()
		self.wm2.disconnect()
		
	def refresh(self):
		data1 	 = self.wm1.get_data() 
		data2	 = self.wm2.get_data()
		pos,axis = self.parser.parse_double(data1,data2)
		if pos and axis:
			for l in self.listeners:
				l.refresh(pos,axis)
			
			
	def register(self, listener):
		self.listeners += [listener]
		
class Single_Talker:
	
	def __init__(self,address):

		## Create a manager for them. Handles the Backend for the wiimotes.
		evDis = EVDispatcher()
		self.wm1 = WMManager( address, evDis ) # Handles the Wiimote; connects to it, manages wiimote state and mode, parses wiimote reports

		
		self.parser = IRparser()
		self.listeners = []
		
	def connect(self):
		print "Searching for wiimotes"
		return self.wm1.connect() and self.wm1.setup() 
				
	
	def disconnect(self): 
		self.wm1.disconnect()

		
	def refresh(self):
		data 	 = self.wm1.get_data() 
		pos,axis = self.parser.parse_single(data)
		if pos and axis:
			for l in self.listeners:
				l.refresh(pos,axis)
			
			
	def register(self, listener):
		self.listeners += [listener]
		
class Printer:
	def refresh(self,(x,y,z),(dx,dy,dz)):
			print "%i,%i,%i,%i,%i" % (1,x,y,x+dx,y+dy)
				
