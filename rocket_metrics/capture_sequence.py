import time
import picamera
import os

FRAMERATE_FPS = 30
DURATION_SEC = 10
frames = FRAMERATE_FPS * DURATION_SEC

def filenames():
    frame = 0
    while frame < frames:
        yield os.path.join(os.path.expanduser('~'), 'capture', 'image%02d.jpg') % frame
        frame += 1

with picamera.PiCamera() as camera:
    camera.resolution = (1024, 768)
    camera.framerate = FRAMERATE_FPS
    camera.start_preview()
    # Give the camera some warm-up time
    time.sleep(2)
    start = time.time()
    camera.capture_sequence(filenames(), use_video_port=True)
    finish = time.time()
print('Captured %d frames at %.2ffps' % (
    frames,
    frames / (finish - start)))