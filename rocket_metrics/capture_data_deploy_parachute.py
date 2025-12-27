#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime
import os
import sys
import subprocess
import logging
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
        logging.info("BUTTON PUSH: Start recording")
        #GPIO.output(LED_UP_PIN, GPIO.LOW)
        PREVIOUS_FLAG = "Record"
    elif PREVIOUS_FLAG == "Record":
        logging.info("BUTTON PUSH: Stop recording & clean GPIO")
        #GPIO.output(LED_UP_PIN, GPIO.HIGH)
        GPIO.output(LED_UP_PIN, GPIO.LOW)
        GPIO.output(LED_DOWN_PIN, GPIO.LOW)
        GPIO.cleanup()
        camera.stop_preview()
        #sys.exit()
        LOOP_FLAG = False

if __name__ == '__main__':
    # Setup logging to both file and console
    log_dir = os.path.join(os.path.expanduser('~'), 'rocket-buds', 'data', 'sensor_measurements')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_filename = os.path.join(log_dir, f"rocket_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure logging with both file and console handlers
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info("="*60)
    logging.info("ROCKET PARACHUTE DEPLOYMENT SYSTEM")
    logging.info("="*60)
    logging.info(f"Log file: {log_filename}")
    
    # Kill any zombie camera processes and stale Python scripts
    logging.info("[INIT] Cleaning up any existing camera processes...")
    try:
        subprocess.run(['sudo', 'killall', '-9', 'raspivid'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.run(['sudo', 'killall', '-9', 'raspistill'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.run(['sudo', 'killall', '-9', 'raspiyuv'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        # Kill any python processes using picamera (except this one)
        subprocess.run(['sudo', 'fuser', '-k', '/dev/vchiq'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        time.sleep(2)
        logging.info("[INIT] Camera cleanup complete")
    except Exception as e:
        logging.warning(f"[INIT] Camera cleanup error (non-critical): {e}")
    
    # Assert dirs for data storage are available
    logging.info("[INIT] Setting up data directories...")
    sensor_dir = os.path.join(os.path.expanduser('~'), 'rocket-buds', 'data', 'sensor_measurements')
    if not os.path.exists(sensor_dir):
        os.makedirs(sensor_dir)
        logging.info(f"[INIT] Created sensor directory: {sensor_dir}")
    else:
        logging.info(f"[INIT] Using existing sensor directory: {sensor_dir}")
    capture_dir = os.path.join(os.path.expanduser('~'), 'rocket-buds', 'data', 'captures')
    if not os.path.exists(capture_dir):
        os.makedirs(capture_dir)
        logging.info(f"[INIT] Created capture directory: {capture_dir}")
    else:
        logging.info(f"[INIT] Using existing capture directory: {capture_dir}")

    # Initialize sensors and get ground altitude
    logging.info("[INIT] Initializing MPU6050 gyro/accelerometer sensor...")
    mpu6050_sensor = mpu6050(0x68)
    logging.info("[INIT] MPU6050 initialized successfully")
    
    logging.info("[INIT] Initializing BMP388 temperature/pressure/altitude sensor...")
    bmp388_sensor = BMP388()
    logging.info("[INIT] BMP388 initialized successfully")
    
    logging.info("[INIT] Warming up sensors for 3 seconds...")
    time.sleep(3) # warmup
    _, _, altitude = bmp388_sensor.get_temperature_and_pressure_and_altitude()
    ground_alt_m = altitude / 100.0
    logging.info(f"[INIT] Ground altitude calibrated: {ground_alt_m:.2f} m")

    # Setup GPIO for charge relay activation
    logging.info("[INIT] Setting up GPIO pins...")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CHARGE_PIN, GPIO.OUT)
    logging.info(f"[INIT] GPIO pin {CHARGE_PIN} configured for CHARGE relay")
    GPIO.setup(LED_UP_PIN, GPIO.OUT)
    logging.info(f"[INIT] GPIO pin {LED_UP_PIN} configured for UP LED")
    GPIO.setup(LED_DOWN_PIN, GPIO.OUT)
    logging.info(f"[INIT] GPIO pin {LED_DOWN_PIN} configured for DOWN LED")
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    logging.info(f"[INIT] GPIO pin {BUTTON_PIN} configured for BUTTON input")
    
    # Remove any existing edge detection before adding new one
    try:
        GPIO.remove_event_detect(BUTTON_PIN)
    except:
        pass
    
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=button_callback, bouncetime=1000)
    logging.info("[INIT] Button event detection enabled")

    # Initialize camera with retry logic
    camera = None
    for attempt in range(3):
        try:
            camera = PiCamera()
            logging.info(f"Camera initialized successfully on attempt {attempt + 1}")
            break
        except Exception as e:
            logging.error(f"Camera initialization attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                logging.error("Failed to initialize camera after 3 attempts. Exiting.")
                GPIO.cleanup()
                sys.exit(1)

    try:
        logging.info("[INIT] Starting camera preview...")
        camera.start_preview()
        logging.info("[INIT] Camera preview started")

        # Open data file and add header
        csv_filename = get_curr_time() + ".csv"
        csv_filepath = os.path.join(sensor_dir, csv_filename)
        logging.info(f"[INIT] Creating data file: {csv_filename}")
        with open(csv_filepath, mode="w") as file:
            file.write('time_curr,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temp_c,pres_pa,alt_m,ignition_status\n')
            logging.info("[INIT] CSV header written")

            previous_1_alt_m = ground_alt_m
            previous_2_alt_m = ground_alt_m
            previous_3_alt_m = ground_alt_m

            start_run_time = time.time()
            ignition_status = ""
            
            logging.info("\n" + "="*60)
            logging.info("SYSTEM READY - Press button to start recording")
            logging.info("="*60 + "\n")

            #while True:
            while LOOP_FLAG:
                if PREVIOUS_FLAG == "Standby":
                    # Blink LEDs in standby mode
                    GPIO.output(LED_UP_PIN, GPIO.HIGH)
                    GPIO.output(LED_DOWN_PIN, GPIO.LOW)
                    time.sleep(0.5)
                    GPIO.output(LED_UP_PIN, GPIO.LOW)
                    GPIO.output(LED_DOWN_PIN, GPIO.HIGH)
                    time.sleep(0.5)
                elif PREVIOUS_FLAG == "Record":
                    # Gather data at 2 Hz
                    time.sleep(0.5)

                    logging.debug("[DATA] Reading sensors...")
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
                    logging.debug(f"[CAMERA] Capturing image: {time_curr}.jpg")
                    camera.capture(img_path, format='jpeg', use_video_port=False, resize=None, quality=85, thumbnail=None, bayer=False)

                    attitude = "UP" if current_alt_m > previous_1_alt_m else "DOWN"
                    logging.info(f'[STATUS] {time_curr}: Alt={current_alt_m:.2f}m (Δ{current_alt_m - previous_1_alt_m:+.2f}m) Temp={temp_c:.1f}°C Pres={pres_pa:.1f}Pa - {attitude}')

                    # Arm CHARGE & LEDs when at least 10m above ground
                    if MINIMUM_SAFE_HEIGHT_m + MEASUREMENT_ERROR_m < current_alt_m:
                        safe_height = MINIMUM_SAFE_HEIGHT_m + MEASUREMENT_ERROR_m
                        logging.info(f"[ARMED] Above minimum safe height ({safe_height:.1f}m threshold)")

                        # Illuminate LEDs according to rocket attitude
                        if current_alt_m > previous_1_alt_m:
                            GPIO.output(LED_UP_PIN, GPIO.HIGH)
                            GPIO.output(LED_DOWN_PIN, GPIO.LOW)
                            logging.debug("[LED] UP indicator ON")
                        else:
                            GPIO.output(LED_UP_PIN, GPIO.LOW)
                            GPIO.output(LED_DOWN_PIN, GPIO.HIGH)
                            logging.debug("[LED] DOWN indicator ON")

                        # Activate charge if altitude is not increasing for 3 measurements and spark has not been lit before
                        if (current_alt_m < previous_1_alt_m) and (current_alt_m < previous_2_alt_m) and (current_alt_m < previous_3_alt_m) and ignition_status == "":
                            logging.warning(f"[DEPLOY] Descent detected for 3 consecutive measurements!")
                            logging.warning(f"[DEPLOY]   Current: {current_alt_m:.2f}m")
                            logging.warning(f"[DEPLOY]   Prev-1: {previous_1_alt_m:.2f}m")
                            logging.warning(f"[DEPLOY]   Prev-2: {previous_2_alt_m:.2f}m")
                            logging.warning(f"[DEPLOY]   Prev-3: {previous_3_alt_m:.2f}m")
                            logging.warning(f"[DEPLOY] Waiting {CHARGE_DELAY_s}s before ignition...")
                            time.sleep(CHARGE_DELAY_s)
                            GPIO.output(CHARGE_PIN,  GPIO.HIGH)
                            start_spark_time = time.time()
                            logging.critical(f"[IGNITION] *** PARACHUTE DEPLOYMENT INITIATED *** (Duration: {SPARK_DURATION_s}s)")
                            ignition_status = "Start"
                            END_SPARK = True
                    else: # Unarm LEDs if below min safe height
                        GPIO.output(LED_UP_PIN, GPIO.LOW)
                        GPIO.output(LED_DOWN_PIN, GPIO.LOW)
                        logging.debug(f"[DISARMED] Below safe height ({current_alt_m:.2f}m < {MINIMUM_SAFE_HEIGHT_m + MEASUREMENT_ERROR_m:.1f}m)")

                    # Stop spark after 2 seconds
                    if END_SPARK:
                        elapsed = time.time() - start_spark_time
                        if elapsed >= SPARK_DURATION_s:
                            GPIO.output(CHARGE_PIN,  GPIO.LOW)
                            logging.critical(f"[IGNITION] *** PARACHUTE DEPLOYMENT COMPLETE *** (Ran for {elapsed:.1f}s)")
                            ignition_status = "Stop"
                            END_SPARK = False

                    # Write measurements to file
                    measurement_str = f'{time_curr},{accel_x},{accel_y},{accel_z},{gyro_x},{gyro_y},{gyro_z},{temp_c},{pres_pa},{current_alt_m},{ignition_status}\n'
                    file.write(measurement_str)
                    logging.debug(f"[DATA] Measurement written to CSV")

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
                        
    except KeyboardInterrupt:
        logging.info("\n[EXIT] Script interrupted by user")
    except Exception as e:
        logging.error(f"[ERROR] Error occurred: {e}")
        import traceback
        logging.error(traceback.format_exc())
    finally:
        logging.info("[CLEANUP] Shutting down...")
        if camera:
            try:
                logging.info("[CLEANUP] Stopping camera preview...")
                camera.stop_preview()
                camera.close()
                logging.info("[CLEANUP] Camera closed")
            except Exception as e:
                logging.error(f"[CLEANUP] Camera cleanup error: {e}")
        logging.info("[CLEANUP] Cleaning up GPIO...")
        GPIO.cleanup()
        logging.info("[CLEANUP] Complete. Exiting.")
        sys.exit()
