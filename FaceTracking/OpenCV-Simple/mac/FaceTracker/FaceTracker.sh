#!/bin/sh

# FaceTracker.sh
# FaceTracker
#
# Created by Christian Muise on 25/01/08.
#  Copyright (c) 2008 Christian Muise. All rights reserved.

cp ../MacOS/FaceTracker .
./FaceTracker | python DataClient.py