#!/usr/bin/python

import RPi.GPIO as GPIO
import sys

channel = 26
LED_UP_PIN = 16
loop_flag = True
previous_flag = "Standby"

def button_callback(channel):
    print("Button was pushed!")
    global loop_flag
    global previous_flag
    if previous_flag == "Standby":
        #GPIO.output(LED_UP_PIN, GPIO.LOW)
        print("Set GPIO")
        previous_flag = "Record"
    elif previous_flag == "Record":
        #GPIO.output(LED_UP_PIN, GPIO.HIGH)
        print("Clean GPIO")
        loop_flag = False
        #previous_flag = "Standby"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_UP_PIN, GPIO.OUT)

GPIO.add_event_detect(channel,GPIO.RISING,callback=button_callback,bouncetime=1000)

while loop_flag:
    if previous_flag == "Standby":
        print("Standby")
    elif previous_flag == "Record":
        print("Record")

#message = input("Do sth")

GPIO.cleanup()
sys.exit()
