import sys

sys.path.append(".")

from Tkinter import *
from final.Wiimote3dTracking import Wiimote3dTracker
from final.Listeners import *
import time

class App:
	
	def __init__(self,master,img):             
		
		frameForDiarams = Frame(master)
		self.frameForDiarams = frameForDiarams
		frameForDiarams.grid(row = 0,column=0,rowspan = 2)
		
		self.diagram = Canvas(frameForDiarams,height =250,width = 600) 
		self.wiimoteButtons = []
		self.diagram.pack(side = TOP)

		
		frameForButtons =Frame(master)
		self.frameForButtons= frameForButtons
		self.master = master
		frameForButtons.grid(row = 0,column = 0,sticky = W)
		
		self.helpfulMessage = Text()
		self.helpfulLabel = Message(master,width = 300,text = "Click 'Search' to begin searching for wiimotes")#self.helpfulMessage)
		self.helpfulLabel.grid(row = 4,sticky=N)	
		
		
		## A button to search for wiimotes
		self.searchButton = Button(frameForButtons, text="Search", command = self.search)
		self.searchButton.grid(row = 0,column = 0,sticky = W)
		
		## A button to conect to wiimotes
		self.connectButton = Button(frameForButtons, text="Connect", command = self.connect)
		self.connectButton.grid(row = 0,column = 1,sticky = E)
		
		self.listOfAdrs = [] ## a list of all the wiimotes we know about.
		self.listOfAdrsButton = Listbox(master,width = 17,selectmode = MULTIPLE)
		self.listOfAdrsButton.grid(row = 1,column = 0,columnspan = 2,sticky = W)
	
		self.frameForDots = Frame()
		self.frameForDots.grid(row = 2,columnspan  =2 )
		self.dotsButton = Button(self.frameForDots,text = "Dots", command = self.toggleDots)
		self.dotsButton.grid(column = 0, sticky = E)
		self.dotsOn = False
		
		self.tracker = None ## This will be a 3D tracker. 
		
	def search(self):
		l =  Wiimote3dTracker.search()
		## l is a list of all wiimotes in range
		if len(l) >0:
			self.updatelistOfAdrs(l)
			return True
		return False
			
	def connect(self):
		
		## Connect to the addresses selected in the list
		selectedAddresses = [self.listOfAdrs[int(i)] for i in self.listOfAdrsButton.curselection()]
		if len(selectedAddresses) ==0: return
		self.tracker =  Wiimote3dTracker( selectedAddresses ) ## Create a 3d tracker, bound to the 
		## selected addresses
		if self.tracker.connect():
		
			self.connectButton.destroy()
			self.disconnectButton = Button(self.frameForButtons, text = "Disconnect", fg = "red", command = self.disconnect)
			self.disconnectButton.grid(row = 0,column = 1,sticky = E)
			
			#self.calibrateButton = Button(self.frameForButtons, text="calibrate", command = self.tracker.calibrate)
			#self.calibrateButton.pack(side=LEFT)
			for adr in selectedAddresses:
				self.createButton(adr,150,76 +16*self.listOfAdrs.index(adr))
			self.tracker.register(Printer())
			self.tracker.start()	
			
	def toggleDots(self):
		if self.dotsOn:
			self.dots.destroy()
			if self.tracker: 
				self.tracker.unregister(self)
			self.dotsOn = False
		else:
			
			self.dots = Canvas(self.frameForDots,height = 600,width = 800)
			self.dot1 = self.dots.create_oval(0,0,0,0,fill = "black")
			self.dot2 = self. dots.create_oval(0,0,0,0,fill = "black")
			self.dots.grid(row = 2,columnspan = 2)
			if self.tracker:
				self.tracker.register(self)
			self.dotsOn = True
			
	def disconnect(self):
		self.tracker.disconnect()
		self.disconnectButton.destroy()
		#self.calibrateButton.destroy()
		self.connectButton = Button(self.frameForButtons, text="Connect", command = self.connect)
		self.connectButton.grid(row = 0,column = 1,sticky = E)
		self.destroyWiimoteButtons()
		
	def updatelistOfAdrs(self,listOfAdrsButton):
		for adr in listOfAdrsButton:
			if adr not in self.listOfAdrs:
				self.listOfAdrs += [adr]
		self.listOfAdrsButton.delete(0, END)
		for a in self.listOfAdrs:
			self.listOfAdrsButton.insert(END, a)

	def refresh(self,(x1,y1,z1),(x2,y2,z2))	:
		## Giving the App class a refrech method means it can 
		## be registered as a listener.
		self.dots.coords(self.dot1, x1,y1,x1+3,y1+3)		
		self.dots.coords(self.dot2, x2,y2,x2+3,y2+3)
		return True
		
	def vibrate(self,duration = 1):
		selectedAddresses = [self.listOfAdrs[int(i)] for i in self.listOfAdrsButton.curselection()]
		for adr in selectedAddresses:
			self.tracker.vibrate(adr,duration)
		
	def createButton(self,address,x,y):	
		b = Button(height=10,width = 40,image = img,command = (lambda a = address: self.tracker.vibrate(address,0.5)))
		w = self.diagram.create_window(x,y,window = b)
		self.diagram.update()
		self.wiimoteButtons += [(b,w)]
	def destroyWiimoteButtons(self):
		for (wb,w) in self.wiimoteButtons:
			wb.destroy()
		wiimoteButtons = []
if __name__ == "__main__":
	root = Tk()
	img = PhotoImage(file = "wiimote40.gif")         
	app = App(root,img)
	root.mainloop()
