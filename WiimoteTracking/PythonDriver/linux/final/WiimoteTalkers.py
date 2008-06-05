#from wmd.WMManager import WMManager
from Wiimote import Wiimote
from IRparser import IRParserFactory


class Talker:
	
	def __init__(self,*addresses):
		## Accepts an arbitrary number of wiimote addresses as an argument
		## Currently, any remotes past the first two are ignored, as the IR
		## parser doesn't know what to do with them. Niether do I actually...
		
		self.adrs=addresses
		if len(self.adrs) ==0 : self.adrs = self.search()
		self.wiimotes= [Wiimote(adr) for adr in self.adrs]
		self.parser = IRParserFactory(len(self.wiimotes))
		self.listeners = []
		
	def connect(self):
		## Tries to connect to each address and returns true if everything went ok.
		## TODO: if self.adrs is empty, do a sweep and find all willing remotes in range.
		print "Connecting to wiimotes..."
		return 	reduce(lambda x, y: x and y, [ wm.connect() for wm in self.wiimotes],True)
		
	def search(self):
		from bluetooth import discover_devices,lookup_name
		print "Searching for wiimotes..."
		wiimotes = discover_devices(3)
		## We need to remove any non- wiimotes. it is possible some wiimotes
		## do not pass this check however. 
		wiimotes = filter(lambda x: lookup_name(x) == 'Nintendo RVL-CNT-01', wiimotes)
		print "Found %i" % len(wiimotes)
		return wiimotes
		
	def disconnect(self): 
		print "Disconnecting"
		# Disconnects from all wiimotes.
		for wm in self. wiimotes: wm.disconnect()

		
	def refresh(self):
		try:
			## refresh retrieves the data from each wiimote, parses them and 
			## sends them to whoever is listening via the refresh method.
			data  = [wm.getData() for wm in self.wiimotes]
			
			pos1,pos2 = self.parser.parse(data)
			if pos1 and pos2: ## IR parser may return None...
				result = True
				for l in self.listeners:
					result &= l.refresh(pos1,pos2)
			if not result: 
				self.disconnect()
				import sys
				sys.exit()	
		except KeyboardInterrupt:
			self.disconnect()
			import sys
			sys.exit()	
			
	def register(self, listener):
		## Adds a listener to the talker
		self.listeners += [listener]
		
		
		
		

	
	
