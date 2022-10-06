#!/usr/bin/python3

import json
import os
import pygame
from pyduinobridge import Bridge_py
import urllib.request as urllib2
from urllib.parse import urlencode
from time import sleep, time


db_url = ''
success_db = False
success_img = False
ssh = True #enable if running through ssh

#display settings
output_w = 1280
output_h = 720
size = (output_w, output_h)
flags = pygame.FULLSCREEN
display = None
visualization = None
font = None
font_countdown = None
white = (255, 255, 255)

# data
keys_array = []
url_img = ''
data_date = ''
data_lux = 0
data_rms = 0
data_rmf = 0

# pyduino settings
serPort = '/dev/ttyACM0'
baudRate = 115200
myBridge = None

#tesla coil vars - ( 0 MAX, 180 MIN ) -> abs(-180 to 0)
isFiring = False
vol_in_rng = (68, 8000)
vol_out_rng = (-180, -150)
vol_in = vol_in_rng[1] - vol_in_rng[0]
vol_out = vol_out_rng[1] - vol_out_rng[0]
freq_in_rng = (-35.0, 0.0)
freq_out_rng = (-180, -5)
freq_in = freq_in_rng[1] - freq_in_rng[0]
freq_out = freq_out_rng[1] - freq_out_rng[0]

# States
run = True
isCooling = False
isDrawing = True
endDrawing = False
data_index = 0


if db_url == '':
    with open('..testData/url.txt') as url_file:
        db_url = url_file.read()


def download_db(url):
    global success_db

    if not success_db:
        # clean first
        if os.path.exists('../Data/db_origin.json'):
            os.system('rm -rf ../Data/*')
            os.system('rm -rf ../Images/*')
            print('Cleaning data folder...')

        # download db
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)

        if response.getcode() == 200:
            print('DB downloaded')
            data = response.read()
            data = data.decode('utf8').replace("'", '"')
            data = json.loads(data)
            
            with open('../Data/db_origin.json', 'w') as json_origin:
                json.dump(data, json_origin)

            print('Getting Pics ...')
            success_db = True
            extract_images()
        else:
            success_db = False
            print('Error downloading db')
    else:
        extract_images()


def extract_images():
    global success_img
    global keys_array

    if not success_img:
        with open('../Data/db_origin.json') as json_origin:
            data_origin = json.load(json_origin)
            data_local = data_origin

            for key, val in data_origin.items():
                keys_array.append(key)
                url = val['image_url']
                filename = url.split('/')[-1]

                #download image
                request = urllib2.Request(url)
                response = urllib2.urlopen(request)
                img_data = response.read()
                if response.getcode() == 200:
                    with open('../Images/'+filename, 'wb') as handler:
                        handler.write(img_data)
                    #update local url
                    data_local[key]['image_url'] = '../Images/'+filename
                else:
                    success_img = False
                    print('Error downloading image: '+filename)
                    print('Will try again in 5"')
                    return

            with open('../Data/db_local.json', 'w') as json_local:
                json.dump(data_local, json_local)
        success_img = True
    else:
        pass




#################### MAINS ####################

while not success_db or not success_img:
    download_db(db_url)
    sleep(5)