# Rocket Buds!
Scripts for model rocket engine thrust measurements and analysis.

## Measurement Instructions
1. Connect RPi and Scale
2. Connect RPi and Powerbank
3. Wait for Command Prompt to appear
4. `cd /home/pi/rocket-buds/thrust_measurement`
5. `sudo python3 thrust_measurement.py`
6. Place KNOWN weight (933.0gr) on scale and remove when requested
7. Place DEAD load (rocket engine) on scale and start measurement
8. IGNITE LOAD
9. `Ctrl+C` to terminate measurement
10. Repeat Steps 5 to 8 for further measurements
11. `sudo shutdown -h now`
12. Unplug RPi to turn off

## Thrust Measurement Stand
- Load Cell Scale
- Cable Protector
- RPi & Monitor
- USB Cable
- Powerbank
- Keyboard & Dongle
- Plastic Enclosure
