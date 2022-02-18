#!/usr/bin/env python

from picamera import PiCamera
from time import sleep
import datetime
import os

camera = PiCamera()
camera.start_preview()
print("Please wait...")
sleep(5)
print("Capturing...")
for i in range(0, 50):
    camera.capture(os.path.join(os.path.expanduser('~'), 'capture', 
                                datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.jpg'))      
print(i)
camera.stop_preview()
print("Image captured successfully")