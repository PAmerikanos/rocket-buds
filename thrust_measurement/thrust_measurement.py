#! /usr/bin/python2
# Based on HX711 for Raspbery Py
import time
from datetime import datetime
import sys, os
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

# Calibrate scale before measurement
print("Initiating scale calibration")
ARBITRARY_REF_UNIT = 350 # Set arbitrary REF_UNIT
hx.set_reference_unit(ARBITRARY_REF_UNIT)
hx.reset()
hx.tare()
hx.get_weight(1) # Get random measurement
time.sleep(3) # Wait for warmup

datetime_str = input("Please enter filename for measurement (YYYYMMDD_DESCRIPTION): ")

KNOWN_MASS = 933.0
input("PLACE known mass (" + str(KNOWN_MASS) + "gr) on scale and press any key when ready.")
time.sleep(1)
relative_weight = hx.get_weight(1) # Get relative weight of known mass using arbitrary REF_UNIT
CALIBRATED_REF_UNIT = int(KNOWN_MASS * ARBITRARY_REF_UNIT / relative_weight)
input("REMOVE known mass from scale and press any key when ready.")
input("PLACE dead load on scale and press any key when ready.")
hx.set_reference_unit(CALIBRATED_REF_UNIT)
hx.reset()
hx.tare()

print("Initiating measurement")

try:
    folder = os.path.join(os.path.expanduser('~'), 'rocket-buds', 'data', 'thrust_measurements')
    #datetime_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file = folder + str(datetime_str) + ".txt"
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
