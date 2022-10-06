#!/usr/bin/python3

import pyaudio
import audioop


DEV_INDEX = 1
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
RECORD_SECONDS = 5

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
		input_device_index=DEV_INDEX,
                input=True,
                frames_per_buffer=CHUNK)


for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    rms = audioop.rms(data, 2)


print(str(rms))

stream.stop_stream()
stream.close()
p.terminate()
