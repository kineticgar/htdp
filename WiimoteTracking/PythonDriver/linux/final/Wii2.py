#!/usr/bin/python -u
# This is largely based on code from:
# WMD 0.1.2 - http://ForTheWiiN.org
# All the major wiimote code is straight from there, but the data parsing, animation
# etc is origonal. Feel free to distribute it. 

import sys
import time
sys.path.append('.')
sys.path.append('./final')

from Animations.Head3D import Scene
from Animations.PyGameBar import Dots
from final.WiimoteTalkers import *

	
		


dt = Double_Talker(address1 = '00:19:FD:ED:E1:25', address2 = '00:19:FD:D7:63:B1')
st = Single_Talker('00:19:FD:D7:63:B1' )
talker = st
assert talker.connect()
#talker.register( Scene()  )
talker.register( Printer() )
#talker.register( Dots() )

try:
	while 1: 
		talker.refresh()
		time .sleep(0.01)
except KeyboardInterrupt:
	talker.disconnect()
	raise
	
import sys
sys.exit()
	
