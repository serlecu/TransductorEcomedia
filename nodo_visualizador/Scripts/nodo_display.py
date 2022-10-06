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


def update_data():
    global endDrawing
    global data_index
    global keys_array

    global url_img
    global data_date
    global data_lux
    global data_rms
    global data_rmf

    key = keys_array[data_index-1]

    if endDrawing:
        data_index = 0
        endDrawing = False
    
    with open('../Data/db_local.json') as json_local:
        data_local = json.load(json_local)
        #update data
        url_img = data_local[key]['image_url']
        data_date = data_local[key]['timestamp']
        data_lux = data_local[key]['light']
        data_rms = data_local[key]['slound']
        data_rmf = data_local[key]['emf']

        #update index or endDrawing
        if data_index >= len(data_local)-1:
            print('End of data_loop')
            endDrawing = True
        else:
            data_index += 1


def cooling(t_cool = 60.0):
    global isCooling
    global isDrawing
    global time_start

    if not isCooling:
        time_start = time()
        isCooling = True
        print("Starting cooling")
    
    draw_cooling(int(t_cool - (time() - time_start)))

    if time() - time_start > t_cool:
        print("Cooling finished")
        isCooling = False
        isDrawing = True


#################### PYGAME ####################

def setup_pygame():
    global display
    global visualization
    global font
    global font_countdown

    # pygame render window
    pygame.init()

    # fonts
    font = pygame.font.Font('freesansbold.ttf', 16)
    font_countdown = pygame.font.Font('freesansbold.ttf', 48)
  
    # set display (for ssh)
    if ssh:
        os.environ["DISPLAY"] = ":0"

    pygame.display.init()
    display = pygame.display.set_mode(size, flags)
    visualization = pygame.Surface(size, pygame.SRCALPHA)
    sleep(2)


def draw_cooling(t_countdown):
    global display

    display.fill((0, 0, 0))

    # set background
    color = (0, 0, 0, 3)
    pygame.draw.rect(visualization, color, pygame.Rect(0, 0, output_w, output_h))

    # draw countdown
    text_countdown = font_countdown.render(str(t_countdown), True, white)
    textRect_countdown = text_countdown.get_rect()
    textRect_countdown.center = size
    display.blit(text_countdown, textRect_countdown)
    pygame.display.update()


def draw_display(image, date, lux, rms, rmf):
    global display

    display.fill((0, 0, 0))

    # set background
    color = (0, 0, 0, 3)
    pygame.draw.rect(visualization, color, pygame.Rect(0, 0, output_w, output_h))
    
    # set image
    img = pygame.image.load(image)
    img = pygame.transform.rotate(img, 180)
    
    # set text-prompts
    text_date = font.render('dateTime: ' + date, True, white)
    text_lux = font.render('lux: '+ str(lux), True, white)
    text_rms = font.render('rms: ' + str(rms), True, white)
    text_rmf = font.render('rmf: ' + str(rmf), True, white)

    textRect_date = text_date.get_rect()
    textRect_date.midleft = (50, 50)
    textRect_lux = text_lux.get_rect()
    textRect_lux.midleft = (50, 75)
    textRect_rms = text_rms.get_rect()
    textRect_rms.midleft = (50, 100)
    textRect_rmf = text_rmf.get_rect()
    textRect_rmf.midleft = (50, 125)
    
    # draw everything
    display.blit(visualization, (0, 0))
    display.blit(img, (0,0))
    display.blit(text_date, textRect_date)
    display.blit(text_lux, textRect_lux)
    display.blit(text_rms, textRect_rms)
    display.blit(text_rmf, textRect_rmf)
    pygame.display.update()


################ COIL ################
# #"<COIL,1,0.0>"

def init_tesla():
    global myBridge

    myBridge = Bridge_py()
    myBridge.begin(serPort, baudRate, numIntValues_FromPy=1, numFloatValues_FromPy=1)
    turn_tesla(True)
    sleep(0.5)
    set_tesla(7000, -10)
    sleep(0.2)
    turn_tesla(False)


def map(value, oldMin, oldMax, newMin, newMax, pre_in = None, pre_out = None):
    if pre_in != None and pre_out != None:
        return (value - oldMin) * (pre_out) / (pre_in) + newMin   
    else:
        return (value - oldMin) * (newMax-newMin) / (oldMax-oldMin) + newMin
    

#TODO: implementar la librería
def turn_tesla(force = True):
    global isFiring
    global myBridge

    if isFiring != force:
        isFiring = force
        dataToArduino = myBridge.write("<COIL,"+str(int(isFiring))+",0.0>")
    
    if isFiring == False:
        set_tesla(0, 0)


#TODO: fallo en el segundo valor (testear fix)   
def set_tesla(vol, freq):
    global myBridge

    vol_mapped = abs(map(int(vol), vol_in_rng[0], vol_in_rng[1], vol_out_rng[0], vol_out_rng[1]))
    freq_mapped = abs(map(float(freq), freq_in_rng[0], freq_in_rng[1], freq_out_rng[0], freq_in_rng[1]))
    dataToArduino = myBridge.write("<COIL,"+str(int(vol_mapped))+","+str(int(freq_mapped))+".0>")



#################### MAINS ####################

# Setup
setup_pygame()
init_tesla()

while not success_db or not success_img:
    download_db(db_url)
    sleep(5)


# Main Loop
while run:

    # 25 FPS
    pygame.time.delay(40)

    for event in pygame.event.get():
        # alt F4
        if event.type == pygame.QUIT:
            run = False

    if isDrawing:
        update_data()
        if endDrawing:
            turn_tesla(False)
            isDrawing = False
        else:
            turn_tesla()
            set_tesla(data_rms, data_rmf)    
            draw_display(url_img, data_date, data_lux, data_rms, data_rmf)
        
    else:
        cooling(60.0)

myBridge.close()
pygame.quit()