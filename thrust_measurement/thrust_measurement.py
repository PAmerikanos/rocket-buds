#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Based on HX711 for Raspbery Py

import time
from datetime import datetime
from tqdm import tqdm
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

# To find ARBITRARY_REF_UNIT:
# 1. Set KNOWN_MASS_gr to the real measured weight and set ARBITRARY_REF_UNIT = 1.
# 2. Place weight on scale.
# 3. Run script once and print out relative_weight.
# 4. Calculate relative_weight/KNOWN_MASS_gr (rerun 2-3 times to get an average).
# 5. Set ARBITRARY_REF_UNIT to the calculated value from #4.
ARBITRARY_REF_UNIT_MAP = [{"type": "BEER KEG", "ref_unit": 40.0, "mass_gr": 5195.0},
                          {"type": "PEACH CAN", "ref_unit": 350.0, "mass_gr": 933.0}]

hx.set_reading_format("MSB", "MSB")

# Calibrate scale before measurement
print("Initiating scale calibration. Select known mass:")
for i, key in enumerate(ARBITRARY_REF_UNIT_MAP):
    print(f"{i} - {key['type']}")
choice = int(input("Enter the number corresponding to the desired option:"))
ARBITRARY_REF_UNIT = ARBITRARY_REF_UNIT_MAP[choice]["ref_unit"]
hx.set_reference_unit(ARBITRARY_REF_UNIT)
hx.reset()
hx.tare()

# Wait for warmup
for _ in tqdm(range(15),desc="Waiting for cell to warm up."):
    time.sleep(1)
hx.get_weight(1) # Get random measurement

exp_desc = input("Please enter experiment description (no spaces): ")

KNOWN_MASS_gr = ARBITRARY_REF_UNIT_MAP[choice]["mass_gr"]
input("PLACE known mass (" + str(KNOWN_MASS_gr) + "gr) on scale and press any key when ready.")
time.sleep(1)
relative_weight = hx.get_weight(1) # Get relative weight of known mass using arbitrary REF_UNIT
print(f"Relative weight: {relative_weight}")
if relative_weight == 0.0:
    print('Unable to measure relative weight. Check scale cables & connection.')
    clean_exit()

CALIBRATED_REF_UNIT = int(KNOWN_MASS_gr * ARBITRARY_REF_UNIT / relative_weight)
input("REMOVE known mass from scale and press any key when ready.")
input("PLACE dead load on scale and press any key when ready.")

for _ in tqdm(range(180),desc="Waiting for cell to stabilize."):
    time.sleep(1)

hx.set_reference_unit(CALIBRATED_REF_UNIT)
hx.reset()
hx.tare()

print("Initiating measurement")

try:
    datetime_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"./measurements/{datetime_str}_{exp_desc}.txt"
    f = open(filename, "a+")
    print("OPENED FILE - Recording")
except Exception as e:
    print(e)
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
