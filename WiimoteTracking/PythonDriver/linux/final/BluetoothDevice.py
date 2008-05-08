"Non-wmd file"
from bluetooth import *
class BluetoothDevice:
	
	
	
	def __init__(self,address):	
		self.address = address
		## Create two bluetooth sockets: 
		##		One to receive data,
		##		One to sent config data
		self.receiveSocket = BluetoothSocket( L2CAP )
		self.sendSocket = BluetoothSocket( L2CAP )
		
	def send(self,data):
		## Data should be a string of hex chars:	
		self.sendSocket.send(data)
