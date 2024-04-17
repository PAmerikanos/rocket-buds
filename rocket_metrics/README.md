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
pip3 install mpu6050-raspberrypi
```

Enable i2c:
```
sudo apt update
sudo apt full-upgrade
sudo apt install -y i2c-tools python3-smbus
sudo raspi-config > Interfacing options
sudo i2cdetect -y 1
```

In `sudo raspi-config` enable I2C and legacy RPIcam

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
### Connect to headless RPi
```
ssh pi@raspberrypi.local
password: 0000
```

### Deploy full capturing and ejection charge
```
python rocket_metrics/capture_data_deploy_parachute.py 
```

### Capture sensor & camera data
```
python rocket-buds/rocket_metrics/capture_camera_gyro_temppresaaltitude.py
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
