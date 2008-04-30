
from wmd.Common import *

class EVDispatcher:

  subs = {}

  
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
    

