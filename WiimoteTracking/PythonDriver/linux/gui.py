from Tkinter import *
from final.WiimoteTalkers import *
from final.Listeners import *
import sys


class App:
	
	def __init__(self,master):
		frame = Frame(master)
		frame.pack()
		self.frame=frame
		
		self.canvas = Canvas(master,height = 600,width = 800)
		self.dot1 = self.canvas.create_oval(0,0,0,0,fill = "black")
		self.dot2 = self. canvas.create_oval(0,0,0,0,fill = "black")
		self.canvas.pack()	
		
		self.searchButton = Button(frame, text="Search", command = self.search)
		self.searchButton.pack(side=LEFT)		
		
		self.connectButton = Button(frame, text="Connect", command = self.connect)
		self.connectButton.pack(side=RIGHT)
		
		self.setOfAdrs = set() ## a list of all the wiimotes we know about.
		self.strOfAdrs = StringVar()
		self.strOfAdrs.set('No Wiimotes Found' )
		self.availableWiimotes = Label(master,textvariable = self.strOfAdrs)
		self.availableWiimotes.pack(side =BOTTOM)
		
	def search(self):
		self.strOfAdrs.set("Searching for wiimotes")
		self.talker  = Talker() 
		if self.talker.getNumberOfWiimotes >0:
			self.updatesetOfAdrs(self.talker.getWiimoteAddress())
			return True
		self.strOfAdrs.set("No Wiimotes Found")
		return False
			
	def connect(self):
		if len(self.setOfAdrs)>0 or self.search():
		## search() returns true iff it found and wiimotes	
			if self.talker.connect():
			## if we can still see hose wiimotes
				self.connectButton.destroy()
				self.disconnectButton = Button(self.frame, text = "Disconnect", fg = "red", command = self.disconnect)
				self.disconnectButton.pack(side = LEFT)
				
				self.callibrateButton = Button(self.frame, text="Callibrate", command = self.talker.callibrate)
				self.callibrateButton.pack(side=LEFT)
				
				self.talker.register(self)
				self.talker.register(Printer())
				self.talker.start()	
			
		
	def disconnect(self):
		self.talker.disconnect()
		self.disconnectButton.destroy()
		self.callibrateButton.destroy()
		self.connectButton = Button(self.frame, text="Connect", command = self.connect)
		self.connectButton.pack(side=LEFT)
		
	def updatesetOfAdrs(self,listOfAdrs):
		for adr in listOfAdrs:
			self.setOfAdrs.add(adr)
		string = ''
		
		for adr in  self.setOfAdrs:
			string += "\n%s" %adr
		self.strOfAdrs.set("Wiimotes in range:"+string)
	
	def refresh(self,(x1,y1,z1),(x2,y2,z2))	:
		## Giving the App class a refrech method means ic can 
		## be registered as a listener.
		self.canvas.coords(self.dot1, x1,y1,x1+3,y1+3)		
		self.canvas.coords(self.dot2, x2,y2,x2+3,y2+3)
		return True

root = Tk()
app = App(root)
root.mainloop()
