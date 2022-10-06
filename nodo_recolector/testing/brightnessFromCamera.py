#!/usr/bin/python3

from picamera2 import Picamera2

import time
import datetime

import numpy as np
from numpy.linalg import norm

#-------------------------------------------
def brightness(img):
    if len(img.shape) == 3:
        # Colored RGB or BGR (*Do Not* use HSV images with this function)
        # create brightness with euclidean norm
        return np.average(norm(img, axis=2)) / np.sqrt(3)
    else:
        # Grayscale
        return np.average(img)

def millis():
	return int(time.time()*1000)
#-------------------------------------------

timeline = millis()
wait = 5000 # ms

camera = Picamera2()
config = camera.create_video_configuration(main={"format": 'XRGB8888', "size": (1920,1080)}, encode="main")
camera.configure(config)
camera.start()

time.sleep(2)

frame = camera.capture_array("main")

loop = True

# capture video stream
while loop:

	if millis() - timeline > wait:
		frame = camera.capture_array("main")
		ct = datetime.datetime.now()

		print(str(ct)+" - CL: "+str(brightness(frame)))

		metadata = camera.capture_file("testing_frame.jpg")

		loop = False


camera.close()
