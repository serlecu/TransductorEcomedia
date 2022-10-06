#!/usr/bin/python3

# import system libraries
import os
import time
import datetime

# import URL handling libraries
import requests
import urllib.request as urllib2
from urllib.parse import urlencode

# import numpy for pixels calculations
import numpy as np
from numpy.linalg import norm

# import matplotlib
import matplotlib.pyplot as plt

#import RtlSdr
from rtlsdr import RtlSdr

# import audio libraries
import pyaudio
import audioop

#import picamera2
from picamera2 import Picamera2

#------------------------------------------------------------------------------
#------------------------------------------- custom methods

# extract brightness from image
def brightness(img):
    if len(img.shape) == 3:
        # Colored RGB or BGR (*Do Not* use HSV images with this function)
        # create brightness with euclidean norm
        return np.average(norm(img, axis=2)) / np.sqrt(3)
    else:
        # Grayscale
        return np.average(img)

# time passed in OF style
def millis():
        return int(time.time()*1000)
#-------------------------------------------
#------------------------------------------------------------------------------

DEBUG = False

# connection vars
auth = "AUTH_KEY"
url = 'https://laboluz.webs.upv.es/marjalStation/saveNewData.php'
saveimg_url = 'https://laboluz.webs.upv.es/marjalStation/saveNewFrame.php'

# data vars
timestamp = datetime.datetime.now().strftime("%H:%M:%S_%d-%m-%Y")
frameTimestamp = datetime.datetime.now().strftime("%H:%M_%d-%m-%Y")
img_path = "/home/laboluz/Scripts/"+str(frameTimestamp)+".jpg"

# audio vars
DEV_INDEX = 1
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
RECORD_SECONDS = 5

audio = pyaudio.PyAudio()
rms = 0

# get USB microphone right index
for ii in range(audio.get_device_count()):
	if audio.get_device_info_by_index(ii).get('name') == "BY-LM40: USB Audio (hw:3,0)":
		DEV_INDEX = ii

# configure RTL-SDR device
sdr = RtlSdr()
sdr.sample_rate = 2.4e6  # Hz
sdr.freq_correction = 60   # PPM
sdr.gain = 'auto'

time.sleep(3)

resolution = 16
minFreq = 800    # MHz 800
maxFreq = 1200  # MHz 1200
DBCut = -27.0
readingsDB = []

# init raspi cam
camera = Picamera2()
config = camera.create_video_configuration(main={"format": 'XRGB8888', "size": (1920,1080)}, encode="main")
camera.configure(config)
camera.start()

time.sleep(3)

frame = camera.capture_array("main")
shine = 0

# time control vars
timeline = millis()
wait = 5000 # ms
loop = True

# this is to make sure the camera is ready
while loop:

    # one shot capture image and calculate brightness
    if millis() - timeline > wait:
            frame = camera.capture_array("main")
            shine = brightness(frame)
            metadata = camera.capture_file(img_path)

            loop = False


time.sleep(3)

# scan ElecroMagnetic frequencies range
for i in np.arange(minFreq, maxFreq, sdr.sample_rate/1e6):
    sdr.center_freq = i*1e6  # Hz
    samples = sdr.read_samples(resolution*1024)
    # use matplotlib to estimate the power spectral density
    power = plt.psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6, color = 'c')

    # save EM spikes in a table
    for v in range(0,len(power[0]),1):
        DB = 10*np.log10(abs(power[0][v]))
        if DB > DBCut:
            readingsDB.append(DB)

# extract average EM power around
avgDB = sum(readingsDB)/len(readingsDB)

# get RMS from microphone
audiostream = audio.open(format=FORMAT,channels=CHANNELS,rate=RATE,input_device_index=DEV_INDEX,input=True,frames_per_buffer=CHUNK)

for i in range(0,int(RATE / CHUNK * RECORD_SECONDS)):
    data = audiostream.read(CHUNK)
    rms = audioop.rms(data,2)

# upload data to DB
payload = {"PASSWORD": auth, 'timestamp': str(timestamp), 'luz': str(round(shine,2)),'sonido': str(rms),'emf': str(round(avgDB,2)), 'image_url': 'https://laboluz.webs.upv.es/marjalStation/frames/'+os.path.basename(img_path)}

if DEBUG:
    print(payload)

# Convert string to byte
payload = urlencode(payload).encode('utf-8')

req = urllib2.Request(url, data=payload)
response = urllib2.urlopen(req)

# testing response
if DEBUG:
    print(response.read())

# upload image
with open(img_path, 'rb') as image_file_descriptor:
    name_img= os.path.basename(img_path)

    data = dict(PASSWORD=auth)
    files= {'marjalFrame': (name_img,image_file_descriptor,'multipart/form-data',{'Expires': '0'}) }
    with requests.Session() as s:
        r = s.post(saveimg_url, files=files, data=data)
        # testing response
        if DEBUG:
            print(r.status_code)
            print(r.text)


# remove local image
if os.path.exists(img_path):
	os.remove(img_path)


# close everything and quit
image_file_descriptor.close()
sdr.close()
camera.close()
