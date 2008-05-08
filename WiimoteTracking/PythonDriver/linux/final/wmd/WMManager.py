from wmd.PyBlueZ import WiimoteBT_PyBlueZ

from wmd.Output import WiimoteMode
from wmd.Common import *


class WMManager:
  go = 1
  subs = {} 
  
  
  def __init__( self, address):
    self.address = address

    self.subscribe( "EV_SHUTDOWN", self.ev_shutdown )

  def connect( self ):
    self.backend = WiimoteBT_PyBlueZ( self.address )
    self.send( *UI_INFO_CONNECTING )
    if self.address and self.backend.connect( self.address ):
      self.mode = WiimoteMode(self.backend )
      self.send( *UI_INFO_CONNECTED )
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
  
  def send( self, evtype, payload ):
    if evtype == WM_IR:
      if self.subs.has_key( evtype ):
        dests = self.subs[evtype]
	for dest in dests:
	  dest( payload )

  def subscribe( self, evtype, callback ):
    if self.subs.has_key( evtype ):
      self.subs[evtype].append( callback )
    else:
      self.subs[evtype] = [ callback ]
