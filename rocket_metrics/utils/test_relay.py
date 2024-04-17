import RPi.GPIO as GPIO
import time

SPARK_DURATION = 2
CHARGE_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(CHARGE_PIN, GPIO.OUT)

GPIO.output(CHARGE_PIN,  GPIO.HIGH)
time.sleep(SPARK_DURATION)
GPIO.output(CHARGE_PIN,  GPIO.LOW)

GPIO.cleanup()
