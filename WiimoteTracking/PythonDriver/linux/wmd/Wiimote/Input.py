import string, time
from copy import copy
from wmd.Common import *

class bf(object):
    def __init__(self,value=0):
        self._d = value

    def __getitem__(self, index):
        return (self._d >> index) & 1 

    def __setitem__(self,index,value):
        value    = (value&1L)<<index
        mask     = (1L)<<index
        self._d  = (self._d & ~mask) | value

    def __getslice__(self, start, end):
        mask = 2L**(end - start) -1
        return (self._d >> start) & mask

    def __setslice__(self, start, end, value):
        mask = 2L**(end - start) -1
        value = (value & mask) << start
        mask = mask << start
        self._d = (self._d & ~mask) | value
        return (self._d >> start) & mask

    def __int__(self):
        return self._d

def decbyte( byte ):
  """Decode byte from two hex chars"""
  d = int(ord( byte.decode("hex") ))
  return d

def toHex(s):
  l = []
  for c in s:
    h = hex(ord(c)).replace('0x', '')
    if len(h) == 1:
      h = '0' + h
    l.append(h)
  return string.join(l, " ")


def hex2s(h):
  return  ('%x' % h).decode("hex")



class WiimoteState:
  """This contains the present state of the Wiimote; buttons, battery, etc."""

  def __init__( self, ev ):
    self.ev = ev

  # These are the button mappings
  buttonmap = {
    '2': 0x0001,
    '1': 0x0002,
    'B': 0x0004,
    'A': 0x0008,
    '-': 0x0010,
    'H': 0x0080,
    'L': 0x0100,
    'R': 0x0200,
    'D': 0x0400,
    'U': 0x0800,
    '+': 0x1000
  }

  buttonstates = {}
  prevbuttonstates = {}
  for bt in buttonmap:
    buttonstates[bt] = 0
    prevbuttonstates[bt] = 0

  def which_buttons( self, rawbtd ):
    btps = []

    if rawbtd != 0:
      for bt in self.buttonmap:
	btk = self.buttonmap[bt]
	if btk & rawbtd:
	  btps.append(bt)

    self.update_button_states( btps )

  def update_button_states( self, btps ):
    bts_up = []
    bts_down = []

    for bt in self.buttonstates:
      self.prevbuttonstates[bt] = self.buttonstates[bt]
      self.buttonstates[bt] = 0

    for bt in btps:
      self.buttonstates[bt] = 1
   
    for bt in self.prevbuttonstates:
      if self.prevbuttonstates[bt] and not self.buttonstates[bt]:
	self.bt_notify(bt, "UP")
	bts_up.append(bt)
      if not self.prevbuttonstates[bt] and self.buttonstates[bt]:
	self.bt_notify(bt, "DOWN")
	bts_down.append(bt)


  def bt_notify( self, bt, state ):
    self.ev.send( WM_BT, [bt, state] )

  REQ20H = 0

