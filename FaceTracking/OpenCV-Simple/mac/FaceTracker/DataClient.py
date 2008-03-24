#
#  DataClient.py
#  FaceTracker
#
#  Created by Christian Muise on 25/01/08.
#  Copyright (c) 2008 Christian Muise. All rights reserved.
#

import sys, socket

mySocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
mySocket.connect ( ( 'localhost', 4440 ) )

while True:
	line = sys.stdin.readline()
	line = line.rstrip('\n')
	if "QUIT" == line:
		break
	if line:
		mySocket.send(line)