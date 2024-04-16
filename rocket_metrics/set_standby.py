#!/usr/bin/python

import RPi.GPIO as GPIO
import sys

channel = 26
LED_UP_PIN = 16
LOOP_FLAG = True
PREVIOUS_FLAG = "Standby"

def button_callback(channel):
    print("Button was pushed!")
    global LOOP_FLAG
    global PREVIOUS_FLAG
    if PREVIOUS_FLAG == "Standby":
        #GPIO.output(LED_UP_PIN, GPIO.LOW)
        #print("Set GPIO")
        PREVIOUS_FLAG = "Record"
    elif PREVIOUS_FLAG == "Record":
        #GPIO.output(LED_UP_PIN, GPIO.HIGH)
        print("Clean GPIO")
        LOOP_FLAG = False

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_UP_PIN, GPIO.OUT)

GPIO.add_event_detect(channel,GPIO.RISING,callback=button_callback,bouncetime=1000)

while LOOP_FLAG:
    if PREVIOUS_FLAG == "Standby":
        print("Standby")
    elif PREVIOUS_FLAG == "Record":
        print("Record")

GPIO.cleanup()
sys.exit()
