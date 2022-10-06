#!/usr/bin/python3

import urllib.request as urllib2
from urllib.parse import urlencode

url = 'https://laboluz.webs.upv.es/marjalStation/getYesterdayData.php'

req = urllib2.Request(url)
response = urllib2.urlopen(req)

# testing response
print(response.read())
