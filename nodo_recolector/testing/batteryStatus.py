#!/usr/bin/python3

from pijuice import PiJuice


pijuice = PiJuice(1, 0x14)
battery = pijuice.status.GetChargeLevel()['data']

print(str(battery))
print(pijuice.status.GetStatus()['data']['battery'])
