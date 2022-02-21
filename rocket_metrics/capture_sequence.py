# https://picamera.readthedocs.io/en/release-1.10/recipes2.html#rapid-capture-and-processing

import time
import picamera
import os

RESOLUTION = (1024, 720) #(1080, 1920)
FRAMERATE_FPS = 30
DURATION_SEC = 10
frames = FRAMERATE_FPS * DURATION_SEC

def filenames():
    frame = 0
    while frame < frames:
        yield os.path.join(os.path.expanduser('~'), 'capture', 'image%02d.jpg') % frame
        frame += 1

with picamera.PiCamera() as camera:
    camera.resolution = RESOLUTION
    camera.framerate = FRAMERATE_FPS
    camera.start_preview()
    # Give the camera some warm-up time
    print("Please wait...")
    time.sleep(2)
    start = time.time()
    print("Capturing")
    camera.capture_sequence(filenames(), use_video_port=True)
    finish = time.time()
print('Captured %d frames at %.2ffps' % (
    frames,
    frames / (finish - start)))