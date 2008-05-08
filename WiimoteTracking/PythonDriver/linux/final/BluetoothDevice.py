from bluetooth import *
class BluetoothDevice:
	"""Contains non wii specific code. Only here to make 
	Wiimote.py look cleaner"""
	
	
	def __init__(self,address):	
		self.address = address
		## Create two bluetooth sockets: 
		##		One to receive data,
		##		One to sent config data
		self.receiveSocket = BluetoothSocket( L2CAP )
		self.sendSocket = BluetoothSocket( L2CAP )
		
	def send(self,data):
		self.sendSocket.send(data)
		
	def getData(self):
  		return self.receiveSocket.recv(1024)

		
	def disconnect(self):
		self.receiveSocket.close()
		self.sendSocket.close()
	
