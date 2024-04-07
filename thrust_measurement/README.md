# Rocket Buds!
Scripts for model rocket engine thrust measurements.

## Measurement Instructions
1. Connect RPi and Scale
2. Connect RPi and Powerbank
3. Switch power ON

On smartphone:

1. Enable hotspot (WiFi `SSID: Pefki / Pass: 1-0`)
2. After RPi connected, run `Net Analyzer > LAN Scan` to determine RPi IP
3. Open JuiceSSH, select RPi IP to connect, 
4. Wait for Command Prompt to appear
5. `cd /rocket-buds/thrust_measurement`
6. `python thrust_measurement.py`
7. Follow onscreen instructions.
8. `Ctrl+C` to terminate measurement
9. Repeat previous steps for further measurements
10. `sudo shutdown now`
11. Unplug RPi to turn off

## Thrust Measurement Stand
- Load Cell Scale
- Cable Protector
- RPi
- USB Cable
- Powerbank
- Plastic Enclosure

## Stuff to bring
- Swiss Army Knife/Multitool
- Electrical Tape
- Water bottle
- Multimeter
- Matches/Lighter
- Known Weight