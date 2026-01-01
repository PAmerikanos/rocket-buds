# Rocket Metrics module

## Setup
- https://desertbot.io/blog/headless-raspberry-pi-zero-w-2-ssh-wifi-setup-mac-windows-10-steps
- https://www.digikey.gr/en/maker/blogs/2021/getting-started-with-the-raspberry-pi-zero-2-w
- https://howchoo.com/pi/how-to-take-a-picture-with-your-raspberry-pi
- https://grantwinney.com/using-pullup-and-pulldown-resistors-on-the-raspberry-pi/
- https://raspberrypi.stackexchange.com/a/108723

To install mpu6050 library:
```
sudo apt-get install python3-pip
sudo -H pip install mpu6050-raspberrypi
```

Enable i2c:
```
sudo apt update
sudo apt full-upgrade
sudo apt install -y i2c-tools python3-smbus
sudo raspi-config > Interfacing options
sudo i2cdetect -y 1
```

In `sudo raspi-config` enable I2C and legacy RPIcam.
Setup Crontab `sudo crontab -e`:
```
@reboot sleep 15; python3 /home/pi/rocket-buds/rocket_metrics/capture_data_deploy_parachute.py >> /home/pi/crontab.log 2>&1
```

### Connections
```
GPIO 23 -> SDA
GPIO 24 -> SCL

MPU 6050 Gyro
    VCC: 5V
    GND: GND
    SCL: GPIO serial clock (I2C)
    SDA: GPIO serial data (I2C)

BMP 388 Temp
    GND: GND
    3Vo: 3.3V
    SCL: GPIO serial clock (I2C)
    SDA: GPIO serial data (I2C)

Charger
    USB: USB cable
    Vout+-: RPi USB/GPIO
    BAT+-: Battery
```


## Operation

1. Set POWER switch to OFF
2. *Optional:* Set ARM switch to CHARGE
3. *Optional:* Connect capacitor leads to 12V (mMotorbike battery)
4. Set ARM switch to OFF
5. Set POWER switch to ON
6. Check RPi/camera/barometer/accelerometer LEDs are on
7. *Optional:* Set ARM switch to ARM
8. Connect to headless RPi
    ```
    ssh pi@raspberrypi.local
    password: 0000
    ```
9. Deploy full capturing and ejection charge
    ```
    python rocket-buds/rocket_metrics/capture_data_deploy_parachute.py 
    ```

## LED Behavior

The system uses two LEDs (LED_UP on GPIO 16 and LED_DOWN on GPIO 20) to indicate the current state:

| State | LED_UP | LED_DOWN | Description |
|-------|--------|----------|-------------|
| **Standby** | Blinking | Blinking | Alternating blink (0.5s interval). Waiting for button press to start recording. |
| **Recording (below safe height)** | OFF | OFF | Recording data but not armed. Altitude < 4.0m (MINIMUM_SAFE_HEIGHT + MEASUREMENT_ERROR). |
| **Armed & Ascending** | ON | OFF | Rocket is climbing. System armed for parachute deployment. |
| **Armed & Descending** | OFF | ON | Rocket is descending. Monitoring for deployment trigger. |
| **Parachute Deployed** | ON | ON | Both LEDs on during ignition sequence (SPARK_DURATION_s). |
| **Shutdown** | OFF | OFF | System stopped via button press or cleanup. |

## Miscellaneous functions
### Capture sensor & camera data
```
python rocket-buds/rocket-buds/rocket_metrics/capture_camera_gyro_temppresaaltitude.py
```

### Capture only video
```
raspivid -o video.h264 -t 10000
```
Capture sequence: 
https://picamera.readthedocs.io/en/release-1.10/recipes2.html#unencoded-image-capture-yuv-format


### Sync sensor & cam data from RPi
```
scp -r pi@raspberrypi.local:/home/pi/rocket-buds/data/ /mnt/SSD_Data/My_Projects/rocket-buds/
```
