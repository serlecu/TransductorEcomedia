#!/usr/bin/python3

import pyaudio

p = pyaudio.PyAudio()

for ii in range(p.get_device_count())
	print(str(ii)+" - "+p.get_device_info_by_index(ii).get('name'))
	if p.get_device_info_by_index(ii).get('name') == "BY-LM40: USB Audio (hw:3,0)":
		print("Found CEPA USB microphone with index: "+str(ii))
