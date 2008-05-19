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
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


from bluetooth import BluetoothSocket,L2CAP
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
		## This next line allows us to catch up with the wiimote if it's
		## sending faster than we're reveiving. This needs sorting out. 
		for i in range(4):  self.receiveSocket.recv(19)

		return self.receiveSocket.recv(19)
  		
		
		return result[0]
	def disconnect(self):
		self.receiveSocket.close()
		self.sendSocket.close()
	
