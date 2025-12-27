## Goals

4 mecanum wheel robot controlled by a twin stick controller UI

## Materials

* Raspberry pi zero w
* Motor bonnet
* IMU (Gyro/Compass) OR phone
* USB Battery pack
* USB PD (Power Delivery) Decoy Trigger

## Setup

Raspberry Pi Zero W:

```bash
# 1. Enable I2C interface
sudo raspi-config nonint do_i2c 0

# Faster numpy
sudo apt-get install libatlas-base-dev

# 2. Install the specific library for that Bonnet
pip3 install adafruit-circuitpython-motorkit

# install Flask and SocketIO.
pip install flask flask-socketio eventlet numpy


```

### Power

- [ ] Set USB PD (Power Delivery) Decoy Trigger to 9V.
- [ ] Double check with voltmeter.

### Layout

- [ ] Ensure Mecanum wheels form an 'X' pattern from the top.

### Wiring

- [ ] M1 (Front Left): Connect to Motor Terminal 1
- [ ] M2 (Front Right): Connect to Motor Terminal 2
- [ ] M3 (Back Left): Connect to Motor Terminal 3
- [ ] M4 (Back Right): Connect to Motor Terminal 4