## This file is part of the htdp project as part of Google Summer of Code
## Copyright (C) 2008 Chris Nicholls
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## 

import sys
sys.path.append(".")
from Tkinter import *
from final.Wiimote3dTracking import Wiimote3dTracker
from final.Listeners import *
from final.OpenNewListeners import lookupListener
import time

class App:
	
	def __init__(self,master,img):             
		self.master = master
		self.tracker = None ## This will be a 3D tracker. 
		menu =Menu(master)
		master.config(menu=menu)
		menu.add_command( label="Search", command = self.search)
		menu.add_command( label = "Connect", command = self.connect,state = DISABLED)
		menu.add_command( label = "Calibrate", command = None,state = DISABLED )
		listenersMenu = Menu(menu)
		listenersMenu.add_command( label = "New listener", command = self.newListener)
		menu.add_cascade( label = "Listeners",menu = listenersMenu)
		self.menu = menu
		self.listenersMenu = listenersMenu
		self.listOfListeners = []
		self.listenersState = []
		
		frameForDiarams = Frame(master)
		self.frameForDiarams = frameForDiarams
		frameForDiarams.grid(row = 0,column=0,rowspan = 2)
		
		self.diagram = Canvas(frameForDiarams,height =250,width = 600) 
		self.wiimoteButtons = []
		self.diagram.pack(side = TOP)

		
		self.helpfulMessage = Text()
		self.helpfulLabel = Message(master,width = 300,text = "Click 'Search' to begin searching for wiimotes")#self.helpfulMessage)
		self.helpfulLabel.grid(row = 4,sticky=N)	
		

		self.listOfAdrs = [] ## a list of all the wiimotes we know about.
		self.listOfAdrsButton = Listbox(master,width = 17,selectmode = MULTIPLE)
		self.listOfAdrsButton.grid(row = 0,column = 0,columnspan = 2,sticky = W)

	
		self.frameForDots = Frame()
		self.frameForDots.grid(row = 2,columnspan  =2 )
		self.dotsButton = Button(self.frameForDots,text = "Dots", command = self.toggleDots)
		self.dotsButton.grid(column = 0, sticky = E)
		self.dotsOn = False
		
		
		
	def search(self):
		l =  Wiimote3dTracker.search()
		## l is a list of all wiimotes in range
		if len(l) >0:
			self.updatelistOfAdrs(l)
			self.menu.entryconfig(2,state = ACTIVE) 
			return True
		return False
			
	def connect(self):
		
		## Connect to the addresses selected in the list
		selectedAddresses = [self.listOfAdrs[int(i)] for i in self.listOfAdrsButton.curselection()]
		if len(selectedAddresses) ==0: return
		self.tracker =  Wiimote3dTracker( selectedAddresses ) ## Create a 3d tracker, bound to the 
		## selected addresses
		if self.tracker.connect():
		
			self.menu.entryconfig(2, label = "Disconnect", command = self.disconnect)
			self.menu.entryconfig(3,state = ACTIVE, command = lambda:self.tracker.calibrate((0,0,0),(800,600,100)))
			for listener in self.listOfListeners:
				self.tracker.register(listener)
			for adr in selectedAddresses:
				self.createButton(adr,150,30 +16*self.listOfAdrs.index(adr))
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
		#self.calibrateButton.destroy()
		self.menu.entryconfig(2,label = "Connect", command = self.connect)
		self.menu.entryconfig(3,state = DISABLED)
		self.destroyWiimoteButtons()
		
	def updatelistOfAdrs(self,listOfAdrsButton):
		for adr in listOfAdrsButton:
			if adr not in self.listOfAdrs:
				self.listOfAdrs += [adr]
		self.listOfAdrsButton.delete(0, END)
		for a in self.listOfAdrs:
			self.listOfAdrsButton.insert(END, a)

	def refresh(self,(x1,y1,z1),(x2,y2,z2))	:
		## Giving the App class a refresh method means it can 
		## be registered as a listener.
		self.dots.coords(self.dot1, x1,600-y1,x1+3,600-y1+3)		
		self.dots.coords(self.dot2, x2,600-y2,x2+3,600-y2+3)
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
		
	def newListener(self):
		listener = lookupListener(self.master)
		if listener == None: return
		if listener not in self.listOfListeners:
			self.listOfListeners.append(listener)
			## There HAS to be a better way of doing this next line right? 
			self.listenersMenu.add_checkbutton(label = str(listener).split()[0].split('.')[-1])
			if self.tracker: self.tracker.register(listener)
		

		
if __name__ == "__main__":
	root = Tk()
	#img = PhotoImage(file = "wiimote40.gif")
	img = PhotoImage(file = "bzzz.gif")
	app = App(root,img)
	root.mainloop()
