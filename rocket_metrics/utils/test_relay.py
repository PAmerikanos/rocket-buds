import RPi.GPIO as GPIO
import time

SPARK_DURATION = 2
CHARGE_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(CHARGE_PIN, GPIO.OUT)

print("Config set")
GPIO.output(CHARGE_PIN,  GPIO.HIGH)
print("ON")
time.sleep(SPARK_DURATION)
GPIO.output(CHARGE_PIN,  GPIO.LOW)
print("OFF")

GPIO.cleanup()
