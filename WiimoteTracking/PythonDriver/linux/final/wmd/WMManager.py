from wmd.PyBlueZ import WiimoteBT_PyBlueZ

from wmd.Output import WiimoteMode
from wmd.Common import *
import time
import psyco

psyco.full()

class WMManager:
  go = 1

  def __init__( self, address, ev ):
    self.address = address
    self.ev = ev

    self.ev.subscribe( EV_SHUTDOWN, self.ev_shutdown )

  def connect( self ):
    self.backend = WiimoteBT_PyBlueZ( self.address )
    self.ev.send( *UI_INFO_CONNECTING )
    if self.address and self.backend.connect( self.address ):
      self.mode = WiimoteMode( self.ev, self.backend )
      self.ev.send( *UI_INFO_CONNECTED )
      print "Connected to %s" % self.address
      return 1

  def setup( self ):
    self.mode.ir.on()
    return 1

  def disconnect( self ):
    self.backend.disconnect()

  def ev_shutdown( self, null ):
    self.go = 0
   
  def get_data(self):
  	return self.backend.receive()
  
  
