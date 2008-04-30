import time
from bluetooth import *
from wmd.Common import *

# This is what the Wiimote calls itself (Bluetooth Name)
WIIMOTE_NAME = "Nintendo RVL-CNT-01"

class WiimoteBT_PyBlueZ:
  def __init__( self, address ):
    self.receive_sock = BluetoothSocket( L2CAP )
    self.control_sock = BluetoothSocket( L2CAP )
    self.address = address

  def connect( self, addr ):
    recv_port = 19
    ctrl_port = 17
    self.receive_sock.connect( ( addr, recv_port ) )
    self.control_sock.connect( ( addr, ctrl_port ) )

    if self.receive_sock and self.control_sock:
      time.sleep(0.5)
      return 1

  def disconnect( self ):
    self.receive_sock.close()
    self.control_sock.close()
    print "Disconnected from %s" % self.address 


  def send_command( self, commandcode ):
    fs = ''
    for b in commandcode:
      fs += str(b).encode("hex").upper()  + " "

    self.control_sock.send( commandcode )
    time.sleep(0.001)



  def receive( self ):
    data = self.receive_sock.recv(1024)
    return data

  def find_willing_wiimote( self ):

    bt_devs = discover_devices(lookup_names = True)
    if bt_devs:

      for bt_dev in bt_devs:
	if bt_dev[1] == WIIMOTE_NAME:
	  addr = bt_dev[0]

	  return addr



  def find_wiimote_services( self, addr ):

    servs = find_service( address = addr )
    if servs:

      return servs
    if not servs:

      return 0


