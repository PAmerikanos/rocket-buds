#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime
import os
import sys
from picamera import PiCamera
from mpu6050 import mpu6050
from utils.BMP388_TempPresAlt import BMP388
import RPi.GPIO as GPIO

MINIMUM_SAFE_HEIGHT_m = 3.0 # 3.0
MEASUREMENT_ERROR_m = 1.0 # 1.5
SPARK_DURATION_s = 2.0 # 5.0
CHARGE_DELAY_s = 1.0 #5.0
#AUTO_SHUTDOWN_s = 120.0

END_SPARK = False
TERMINATE_PROCESS = False
LOOP_FLAG = True
PREVIOUS_FLAG = "Standby"

# GPIO pins
CHARGE_PIN = 23
LED_UP_PIN = 16
LED_DOWN_PIN = 20
BUTTON_PIN = 26

def get_curr_time():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def button_callback(channel):
    global LOOP_FLAG
    global PREVIOUS_FLAG
    if PREVIOUS_FLAG == "Standby":
        print("BUTTON PUSH: Start recording")
        #GPIO.output(LED_UP_PIN, GPIO.LOW)
        PREVIOUS_FLAG = "Record"
    elif PREVIOUS_FLAG == "Record":
        print("BUTTON PUSH: Stop recording & clean GPIO")
        #GPIO.output(LED_UP_PIN, GPIO.HIGH)
        GPIO.output(LED_UP_PIN, GPIO.LOW)
        GPIO.output(LED_DOWN_PIN, GPIO.LOW)
        GPIO.cleanup()
        camera.stop_preview()
        #sys.exit()
        LOOP_FLAG = False

if __name__ == '__main__':
    # Assert dirs for data storage are available
    sensor_dir = os.path.join(os.path.expanduser('~'), 'rocket-buds', 'data', 'sensor_measurements')
    if not os.path.exists(sensor_dir):
        os.makedirs(sensor_dir)
    capture_dir = os.path.join(os.path.expanduser('~'), 'rocket-buds', 'data', 'captures')
    if not os.path.exists(capture_dir):
        os.makedirs(capture_dir)

    # Initialize sensors and get ground altitude
    mpu6050_sensor = mpu6050(0x68)
    bmp388_sensor = BMP388()
    time.sleep(3) # warmup
    _, _, altitude = bmp388_sensor.get_temperature_and_pressure_and_altitude()
    ground_alt_m = altitude / 100.0

    # Setup GPIO for charge relay activation
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CHARGE_PIN, GPIO.OUT)
    GPIO.setup(LED_UP_PIN, GPIO.OUT)
    GPIO.setup(LED_DOWN_PIN, GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # Remove any existing edge detection before adding new one
    try:
        GPIO.remove_event_detect(BUTTON_PIN)
    except:
        pass
    
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=button_callback, bouncetime=1000)

    try:
        # Initialize PiCamera for image capturing
        with PiCamera() as camera:
            camera.start_preview()

            # Open data file and add header
            with open(os.path.join(sensor_dir, get_curr_time() + ".csv"), mode="w") as file:
                file.write('time_curr,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temp_c,pres_pa,alt_m,ignition_status\n')

                previous_1_alt_m = ground_alt_m
                previous_2_alt_m = ground_alt_m
                previous_3_alt_m = ground_alt_m

                start_run_time = time.time()
                ignition_status = ""

                #while True:
                while LOOP_FLAG:
                    if PREVIOUS_FLAG == "Standby":
                        GPIO.output(LED_UP_PIN, GPIO.HIGH)
                        GPIO.output(LED_DOWN_PIN, GPIO.LOW)
                        time.sleep(0.5)
                        GPIO.output(LED_UP_PIN, GPIO.LOW)
                        GPIO.output(LED_DOWN_PIN, GPIO.HIGH)
                        time.sleep(0.5)
                    elif PREVIOUS_FLAG == "Record":
                        # Gather data at 2 Hz
                        time.sleep(0.5)

                        accel_data = mpu6050_sensor.get_accel_data()
                        gyro_data = mpu6050_sensor.get_gyro_data()
                        temperature, pressure, altitude = bmp388_sensor.get_temperature_and_pressure_and_altitude()

                        time_curr = get_curr_time()
                        accel_x = accel_data['x']
                        accel_y = accel_data['y']
                        accel_z = accel_data['z']
                        gyro_x = gyro_data['x']
                        gyro_y = gyro_data['y']
                        gyro_z = gyro_data['z']
                        temp_c = temperature / 100.0
                        pres_pa = pressure / 100.0
                        current_alt_m = altitude / 100.0 - ground_alt_m

                        # Write photos to file
                        img_path = os.path.join(capture_dir, time_curr + '.jpg')
                        camera.capture(img_path, format='jpeg', use_video_port=False, resize=None, quality=85, thumbnail=None, bayer=False)

                        attitude = "UP" if current_alt_m > previous_1_alt_m else "DOWN"
                        print(f'{time_curr}: RECORDING & CAPTURING @{current_alt_m}m - {attitude}')

                        # Arm CHARGE & LEDs when at least 10m above ground
                        if MINIMUM_SAFE_HEIGHT_m + MEASUREMENT_ERROR_m < current_alt_m:
                            print("ARMED: Above minimum safe height")

                            # Illuminate LEDs according to rocket attitude
                            if current_alt_m > previous_1_alt_m:
                                GPIO.output(LED_UP_PIN, GPIO.HIGH)
                                GPIO.output(LED_DOWN_PIN, GPIO.LOW)
                            else:
                                GPIO.output(LED_UP_PIN, GPIO.LOW)
                                GPIO.output(LED_DOWN_PIN, GPIO.HIGH)

                            # Activate charge if altitude is not increasing for 3 measurements and spark has not been lit before
                            if (current_alt_m < previous_1_alt_m) and (current_alt_m < previous_2_alt_m) and (current_alt_m < previous_3_alt_m) and ignition_status == "":
                                time.sleep(CHARGE_DELAY_s)
                                GPIO.output(CHARGE_PIN,  GPIO.HIGH)
                                start_spark_time = time.time()
                                print("IGNITION: Start")
                                ignition_status = "Start"
                                END_SPARK = True
                        else: # Unarm LEDs if below min safe height
                                GPIO.output(LED_UP_PIN, GPIO.LOW)
                                GPIO.output(LED_DOWN_PIN, GPIO.LOW)

                        # Stop spark after 2 seconds
                        if END_SPARK:
                            if time.time() - start_spark_time >= SPARK_DURATION_s:
                                GPIO.output(CHARGE_PIN,  GPIO.LOW)
                                print("IGNITION: Stop")
                                ignition_status = "Stop"
                                END_SPARK = False

                        # Write measurements to file
                        measurement_str = f'{time_curr},{accel_x},{accel_y},{accel_z},{gyro_x},{gyro_y},{gyro_z},{temp_c},{pres_pa},{current_alt_m},{ignition_status}\n'
                        file.write(measurement_str)

                        previous_3_alt_m = previous_2_alt_m
                        previous_2_alt_m = previous_1_alt_m
                        previous_1_alt_m = current_alt_m

                        #if time.time() - start_run_time >= AUTO_SHUTDOWN_s:
                        #if TERMINATE_PROCESS:
                            # GPIO.output(LED_UP_PIN, GPIO.LOW)
                            # GPIO.output(LED_DOWN_PIN, GPIO.LOW)
                            # GPIO.cleanup()
                            # camera.stop_preview()
                            # sys.exit()
                        

    finally:
        GPIO.cleanup()
        sys.exit()
