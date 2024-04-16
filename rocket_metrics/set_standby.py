#!/usr/bin/python

import RPi.GPIO as GPIO

channel = 26
LED_UP_PIN = 16
flag = False

# def loop_A():
#     while True:
#         print("A")

# def loop_B():
#     while True:
#         print("B")

def button_callback(channel):
    print("Button was pushed!")
    global flag
    if flag:
        GPIO.output(LED_UP_PIN, GPIO.LOW)
        flag = False
    else:
        GPIO.output(LED_UP_PIN, GPIO.HIGH)
        flag = True

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_UP_PIN, GPIO.OUT)

GPIO.add_event_detect(channel,GPIO.RISING,callback=button_callback,bouncetime=1000)

while True:
    if flag:
        print("YES")
    elif not flag:
        print("NO")

#message = input("Do sth")

GPIO.cleanup()
