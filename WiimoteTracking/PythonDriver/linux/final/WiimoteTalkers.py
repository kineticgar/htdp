#from wmd.WMManager import WMManager
from Wiimote import Wiimote
from IRparser import IRparser


class Talker:
	
	def __init__(self,*addresses):
		## Accepts an arbitrary number of wiimote addresses as an argument
		## Currently, any remotes past the first two are ignored, as the IR
		## parser doesn't know what to do with them. Niether do I actually...
		
		self.adrs=addresses
		self.wiimotes= [Wimote(adr) for adr in self.adrs]
		self.parser = IRparser()
		self.listeners = []
		
	def connect(self):
		## Tries to connect to each address and returns true if everything went ok.
		## TODO: if self.adrs is empty, do a sweep and find all willing remotes in range.
		return 	reduce(lambda x, y: x and y, [ wm.connect() for wm in self.wiimotes],True)
		
	
	def disconnect(self): 
		# Disconnects from all wiimotes.
		for wm in self. wiimotes: wm.disconnect()

		
	def refresh(self):
		## refresh retrieves the data from each wiimote, parses them and 
		## sends them to whoever is listening via the refresh method.
		data  = [wm.getData() for wm in self.wiimotes]
		
		pos,axis = self.parser.parse(data)
		if pos and axis: ## IR parser may return None...
			for l in self.listeners:
				l.refresh(pos,axis)
			
			
	def register(self, listener):
		## Adds a listener to the talker
		self.listeners += [listener]
		
		
		
		
class Printer:
	## This is an example of a listener. Its refresh method simply prints the data
	def refresh(self,(x,y,z),(dx,dy,dz)):
			print "%i,%i,%i,%i,%i" % (1,x,y,x+dx,y+dy)
				
