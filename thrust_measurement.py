#! /usr/bin/python2
# Based on HX711 for Raspbery Py
import time
from datetime import datetime
import sys
import RPi.GPIO as GPIO
from hx711py.hx711 import HX711


# Pins definitions
led_arm_pin = 13
led_rec_pin = 6
hx = HX711(12,16)

# Set up pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_arm_pin, GPIO.OUT, initial=GPIO.HIGH) # GREEN LED
GPIO.setup(led_rec_pin, GPIO.OUT, initial=GPIO.LOW) # RED LED


def clean_exit():
    GPIO.output(led_arm_pin, GPIO.LOW)
    GPIO.output(led_rec_pin, GPIO.LOW)
    GPIO.cleanup()
    print("STOPPED AND CLEANED GPIO")
    sys.exit()
    GPIO.cleanup()


# Setup load cell params and tare
# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(328)
hx.reset()
hx.tare()
print("TARE SET - Initiating measurement")

try:
    #folder = "/media/pi/paris/Rocketry/Measurements"
    folder = "/home/pi/Rocketry/Measurements/"
    datetime_str = str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    file = folder + datetime_str + ".txt"
    f = open(file,"a+")
    print("OPENED FILE - Recording")
except:
    print("ERROR opening file - Check USB drive")
    clean_exit()


try:
    while True:
        GPIO.output(led_rec_pin, not GPIO.input(led_rec_pin))
        val = hx.get_weight(1)
        print(val)
        f.write(str(time.time()) + ";" + str(val) +  "\n")
except (KeyboardInterrupt, SystemExit):
    print("ERROR recording")
    f.close()
    clean_exit()
