import sys

sys.path.append(".")

from Tkinter import *
from final.Wiimote3dTracking import Wiimote3dTracker
from final.Listeners import *


class App:
	
	def __init__(self,master):
		frame = Frame(master)
		frame.pack()
		self.frame=frame
		
		self.listOfAdrs = [] ## a list of all the wiimotes we know about.
		self.listOfAdrsButton = Listbox(master,selectmode = MULTIPLE)
		self.listOfAdrsButton.pack(side = TOP)
		

		## A button to search for wiimotes
		self.searchButton = Button(frame, text="Search", command = self.search)
		self.searchButton.pack(side=LEFT)		
		
		## A button to connect to wiimotes
		self.connectButton = Button(frame, text="Connect", command = self.connect)
		self.connectButton.pack(side=RIGHT)
		
		
		self.tracker = None ## This will be a 3D tracker. 
		
		## This displays two dots, to represent the two LEDs being tracked
		self.canvas = Canvas(master,height = 600,width = 800)
		self.dot1 = self.canvas.create_oval(0,0,0,0,fill = "black")
		self.dot2 = self. canvas.create_oval(0,0,0,0,fill = "black")
		self.canvas.pack()	
		
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
		self.tracker =  Wiimote3dTracker( selectedAddresses ) ## Create a 3d tracker, bound to the 
		## selected addresses
		if self.tracker.connect():
		
			self.connectButton.destroy()
			self.disconnectButton = Button(self.frame, text = "Disconnect", fg = "red", command = self.disconnect)
			self.disconnectButton.pack(side = LEFT)
			
			self.callibrateButton = Button(self.frame, text="Callibrate", command = self.tracker.callibrate)
			self.callibrateButton.pack(side=LEFT)
			
			self.tracker.register(self)
			self.tracker.register(Printer())
			self.tracker.start()	
				
		
	def disconnect(self):
		self.tracker.disconnect()
		self.disconnectButton.destroy()
		self.callibrateButton.destroy()
		self.connectButton = Button(self.frame, text="Connect", command = self.connect)
		self.connectButton.pack(side=LEFT)
		
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
		self.canvas.coords(self.dot1, x1,y1,x1+3,y1+3)		
		self.canvas.coords(self.dot2, x2,y2,x2+3,y2+3)
		return True
if __name__ == "__main__":
	root = Tk()
	app = App(root)
	root.mainloop()
