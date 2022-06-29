#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import smbus
import math
from mpu6050 import mpu6050

"""
To install mpu6050 library:
    sudo apt-get install python3-pip
    pip3 install mpu6050-raspberrypi

"""


if __name__ == '__main__':
    import time

    sensor = mpu6050(0x68)

    while True:
        time.sleep(0.5)
        accel_data = sensor.get_accel_data()
        gyro_data = sensor.get_gyro_data()
        print('Acceleration:')
        print(accel_data)
        print('Gyro:')
        print(gyro_data)
