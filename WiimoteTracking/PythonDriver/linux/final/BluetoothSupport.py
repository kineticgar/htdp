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
"""This is a group of wrappers for various ooperating systems"""
def newSocket():
		from os import name
		if name == "posix":
			return __LinuxL2CAPSocket()
		if name == "windows": #??? not sure what the name is
			return __WindowsL2CAPSocket()
		if name == "mac": #??? not sure what the name is
			return __MacL2CAPSocket()
		else:
			## Lets try linux...
			Warning("Operating system not recognised")
			return __LinuxL2CAPSocket()
		
		
class __LinuxL2CAPSocket:
	"""Linux L2CAP wrapper"""
	from bluetooth import BluetoothSocket,L2CAP	
	def __init__(self):
		self.sock = self.BluetoothSocket( self.L2CAP )
	
	def connect(self,address,port):
		self.sock.connect((address,port))
		
	def close(self):
		self.sock.close()
		
	def receive(self,length):
		return self.sock.recv(length)
		
	def send(self,string):
		self.sock.send(string)
	
class __WindowsL2CAPSocket():
	"""Windows L2CAP wrapper"""	
	def __init__(self):
		raise OSError("Sorry, Windows is not currently supported") 
	
	def connect(self,address,port):
		pass
		
	def close(self):
		pass
		
	def receive(self,length):
		pass
		
	def send(self,string):
		pass
		
class __MacL2CAPSocket():
	"""Mac L2CAP wrapper"""	
	def __init__(self):
		raise OSError("Sorry, Macs are not currently supported") 
	
	def connect(self,address,port):
		pass
		
	def close(self):
		pass
		
	def receive(self,length):
		pass
		
	def send(self,string):
		pass
