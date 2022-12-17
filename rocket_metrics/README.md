# Rocket Metrics module

## Setup RPi Guides
- https://desertbot.io/blog/headless-raspberry-pi-zero-w-2-ssh-wifi-setup-mac-windows-10-steps
- https://www.digikey.gr/en/maker/blogs/2021/getting-started-with-the-raspberry-pi-zero-2-w
- https://howchoo.com/pi/how-to-take-a-picture-with-your-raspberry-pi

## Operation
### Connect to headless RPi
```
ssh pi@raspberrypi.local
password: 0000
```

### Capture sensor & camera data
```
python rocket_metrics/capture_camera_gyro_temppresaaltitude.py
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