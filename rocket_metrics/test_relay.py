# getting the main GPIO libraly
import RPi.GPIO as GPIO
# getting the time libraly
import time

# setting a current mode
GPIO.setmode(GPIO.BCM)
#removing the warings 
GPIO.setwarnings(False)
#creating a list (array) with the number of GPIO's that we use 
pins = [23]

#setting the mode for all pins so all will be switched on 
GPIO.setup(pins, GPIO.OUT)

#for loop where pin = 18 next 17 ,15, 14 
for pin in pins :
	#setting the GPIO to HIGH or 1 or true
	GPIO.output(pin,  GPIO.HIGH)
	#wait 0,5 second
	time.sleep(2)
	#setting the GPIO to LOW or 0 or false
	GPIO.output(pin,  GPIO.LOW)
	#wait 0,5 second
	time.sleep(2)
	#setting the GPIO to HIGH or 1 or true
	GPIO.output(pin,  GPIO.HIGH)
	#wait 0,5 second
	time.sleep(2)
	#setting the GPIO to LOW or 0 or false
	GPIO.output(pin,  GPIO.LOW)
	#wait 0,5 second
	time.sleep(2)

	#Checking if the current relay is running and printing it 
	if not GPIO.input(pin):
		print("Pin ", str(pin), " is working")

#cleaning all GPIO's 
GPIO.cleanup()
print("Shutdown All relays")
