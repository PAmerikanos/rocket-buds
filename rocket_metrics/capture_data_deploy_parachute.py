#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime
import os
import sys
from picamera import PiCamera
from mpu6050 import mpu6050
from BMP388_TempPresAlt import BMP388
import RPi.GPIO as GPIO

MINIMUM_SAFE_HEIGHT_m = 4.5 # 3.0
MEASUREMENT_ERROR_m = 1.5 # 1.5
SPARK_DURATION_s = 2.0 # 5.0
CHARGE_DELAY_s = 1.0 #5.0
AUTO_SHUTDOWN_s = 120.0

def get_curr_time():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")

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
    END_SPARK = False
    CHARGE_PIN = 23
    LED_UP_PIN = 16
    LED_DOWN_PIN = 20
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(CHARGE_PIN, GPIO.OUT)
    GPIO.setup(LED_UP_PIN, GPIO.OUT)
    GPIO.setup(LED_DOWN_PIN, GPIO.OUT)

    # Initialize PiCamera for image capturing
    with PiCamera() as camera:
        camera.start_preview()

        try:
            # Open data file and add header
            with open(os.path.join(sensor_dir, get_curr_time() + ".csv"), mode="w") as file:
                file.write('time_curr,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temp_c,pres_pa,alt_m,ignition_status\n')

                previous_alt_m = ground_alt_m
                start_run_time = time.time()
                ignition_status = ""

                while True:
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

                    # Illuminate LEDs according to rocket attitude
                    if current_alt_m > previous_alt_m:
                        GPIO.output(LED_UP_PIN, GPIO.HIGH)
                        GPIO.output(LED_DOWN_PIN, GPIO.LOW)
                        attitude = "UP"
                    else:
                        GPIO.output(LED_UP_PIN, GPIO.LOW)
                        GPIO.output(LED_DOWN_PIN, GPIO.HIGH)
                        attitude = "DOWN"

                    print(f'{time_curr}: RECORDING & CAPTURING @{current_alt_m}m - {attitude}')


                    # Activate charge when at least 10m above ground, and altitude is not increasing
                    if MINIMUM_SAFE_HEIGHT_m + MEASUREMENT_ERROR_m < current_alt_m:
                        print("ARMED: Above minimum safe height")
                        if current_alt_m < previous_alt_m - MEASUREMENT_ERROR_m:
                            time.sleep(CHARGE_DELAY_s)
                            GPIO.output(CHARGE_PIN,  GPIO.HIGH)
                            start_spark_time = time.time()
                            print("IGNITION: Start")
                            ignition_status = "Start"
                            END_SPARK = True

                    if END_SPARK:
                        if time.time() - start_spark_time >= SPARK_DURATION_s:
                            GPIO.output(CHARGE_PIN,  GPIO.LOW)
                            print("IGNITION: Stop")
                            ignition_status = "Stop"
                            END_SPARK = False

                    # Write measurements to file
                    measurement_str = f'{time_curr},{accel_x},{accel_y},{accel_z},{gyro_x},{gyro_y},{gyro_z},{temp_c},{pres_pa},{current_alt_m},{ignition_status}\n'
                    file.write(measurement_str)

                    previous_alt_m = current_alt_m

                    if time.time() - start_run_time >= AUTO_SHUTDOWN_s:
                        GPIO.output(LED_UP_PIN, GPIO.LOW)
                        GPIO.output(LED_DOWN_PIN, GPIO.LOW)
                        sys.exit()

        finally:
            camera.stop_preview()
