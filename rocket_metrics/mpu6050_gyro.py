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
        all_data = sensor.get_all_data()
        print('Temperature = %.1fC | Pressure = %.2fPa | Altitude = %.2fm '%(temperature/100.0, pressure/100.0, altitude/100.0))
