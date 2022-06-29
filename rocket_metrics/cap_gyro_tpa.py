#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime
import smbus
import math
from mpu6050 import mpu6050
from BMP388_TempPresAlt import BMP388

"""
To install mpu6050 library:
    sudo apt-get install python3-pip
    pip3 install mpu6050-raspberrypi
"""

def get_curr_time():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")

if __name__ == '__main__':
    import time

    mpu6050_sensor = mpu6050(0x68)
    bmp388_sensor = BMP388()

    print('time_curr; accel_x; accel_y; accel_z; gyro_x; gyro_y; gyro_z; temp_c; pres_pa; alt_m')
    with open(get_curr_time() + ".txt", mode="w") as file:
        while True:
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
            alt_m = altitude / 100.0

            measurement_str = f'{time_curr}; {accel_x}; {accel_y}; {accel_z}; {gyro_x}; {gyro_y}; {gyro_z}; {temp_c}; {pres_pa}, {alt_m}\n'
            file.write(measurement_str)

            print(f'{time_curr}: RECORDING')
