#!/usr/bin/python3

import urllib.request as urllib2
from urllib.parse import urlencode
from pijuice import PiJuice

import psutil
import datetime

DEBUG = False

auth = "AUTH_KEY"
url = 'https://laboluz.webs.upv.es/marjalStation/writeToJson.php'

external_ip = urllib2.urlopen('https://ident.me').read().decode('utf8')

timestamp = datetime.datetime.now().strftime("%H:%M:%S_%d-%m-%Y")

pijuice = PiJuice(1, 0x14)
battery = pijuice.status.GetChargeLevel()['data']

temperature = psutil.sensors_temperatures().get('cpu_thermal')[0].current

memoryUsed = psutil.virtual_memory()[2]

payload = {"PASSWORD": auth, 'ip': external_ip,'timestamp': timestamp,'temperature': temperature, 'memory': memoryUsed, 'battery': str(battery)}

if DEBUG:
    print(payload)

# Convert string to byte
payload = urlencode(payload).encode('utf-8')

req = urllib2.Request(url, data=payload)
response = urllib2.urlopen(req)

if DEBUG:
    print(response.read())
