#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
import RPi.GPIO as GPIO


# GPIO pins
LED_UP_PIN = 16
LED_DOWN_PIN = 20


if __name__ == '__main__':

    # Setup GPIO for charge relay activation
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_UP_PIN, GPIO.OUT)
    GPIO.setup(LED_DOWN_PIN, GPIO.OUT)

    try:
        while True:
            GPIO.output(LED_UP_PIN, GPIO.HIGH)
            GPIO.output(LED_DOWN_PIN, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(LED_UP_PIN, GPIO.LOW)
            GPIO.output(LED_DOWN_PIN, GPIO.HIGH)
            time.sleep(0.5)
                        

    finally:
        GPIO.cleanup()
        sys.exit()
