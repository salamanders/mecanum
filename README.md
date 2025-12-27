## Setup

Raspberry Pi Zero W:

```bash
# 1. Enable I2C interface
sudo raspi-config nonint do_i2c 0

# 2. Install the specific library for that Bonnet
pip3 install adafruit-circuitpython-motorkit

# install Flask and SocketIO.
pip install flask flask-socketio eventlet numpy
```

Set USB PD (Power Delivery) Decoy Trigger to 9V.

