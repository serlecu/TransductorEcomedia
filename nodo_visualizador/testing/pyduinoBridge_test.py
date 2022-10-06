#!/usr/bin/python3

from pyduinobridge import Bridge_py

import time

# pyduino serial port vars
serPort = '/dev/ttyACM0' # <----- set here the right serial port
baudRate = 115200
myBridge = Bridge_py()
myBridge.begin(serPort, baudRate, numIntValues_FromPy=1, numFloatValues_FromPy=1)

# testing Tesl Coil ON/OFF and servo positions

# TESLA COIL ON
dataToArduino = myBridge.write("<COIL,1,0.0>")

time.sleep(0.1)

# SET INTENSIY at 10 AND FREQUENCY at 10 ( 0 MAX, 180 MIN )
dataToArduino = myBridge.write("<DATA,150,10.0>")

time.sleep(5)

# RESET INTENSITY AND FREQUENCY
dataToArduino = myBridge.write("<DATA,180,180.0>")

time.sleep(0.1)

# TESLA COIL OFF
dataToArduino = myBridge.write("<COIL,0,0.0>")

myBridge.close()
