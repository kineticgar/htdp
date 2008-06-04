#! /usr/bin/env python
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

import sys,time
sys.path.append('.')

from final.WiimoteTalkers import *

address = '00:19:FD:ED:E1:25'  ## address of my wiimote
address2 = '00:19:FD:D7:63:B1' ## address of my second wiimote
talker  = Talker(address2) ## Single_Talker talks to  a single wiimote
## A talker has the following methods:
## connect() -- connects to any  wiimotes it knows the address for
## disconnect() -- quite similar to connect. 
##
## register( listener ) 
## refresh()
## a listener is anything that has a refresh(pos ,axis) method. When talker.register( newListener )
## is called, newLitener is added to the list of talkers current listeners. Upon calling 
## talker.refresh() refresh( pos, axis) is called for each of the registered listeners,
## where pos and axis are the processed data from the wiimotes. 

talker.connect() ##Connect to the wiimote

## These are various ways of dealing with the data.
## Scene is a 3D head tracking  scene using python visual
## Printer just prints the position data out to the standard out
## Dots uses pygame to display what the wiimote sees.
from Animations.Head3D import Scene
from Animations.PyGameBar import Dots
#talker.register( Scene()  )
talker.register( Printer() )
talker.register( Dots() )
#
while 1: talker.refresh();#time.sleep(0.01)


	

