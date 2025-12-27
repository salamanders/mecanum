# Robot Twin Stick Controller

4 mecanum wheel robot controlled by a twin stick controller UI.

## Getting Started

### Prerequisites

* Python 3.7+
* Hardware:
    * Raspberry Pi Zero W (or similar)
    * Motor Bonnet
    * Mecanum wheels
    * USB Battery pack
    * USB PD (Power Delivery) Decoy Trigger (set to 9V)
    * IMU (optional) or Android Phone (Pixel 4 etc.) for compass

### System Dependencies (Raspberry Pi)

For `numpy` and hardware access on Raspberry Pi:

```bash
sudo raspi-config nonint do_i2c 0
sudo apt-get install libatlas-base-dev
```

### Installation

1. Clone the repo.
2. Install Python dependencies:

```bash
make install
```

### Running the Robot

Start the server:

```bash
make run
```

Then visit `https://<ROBOT_IP>:5000/controller` on your phone.

### Development (Mock Mode)

If you run this project on a machine without the Motor Bonnet (e.g., your laptop), it will automatically fallback to **Mock Mode**.
In Mock Mode, motor commands are printed to the console instead of trying to talk to I2C hardware.

### Testing

To test motor mappings (or check Mock output):

```bash
make test
```

## Hardware Setup

* **Power**: Set USB PD Trigger to 9V.
* **Layout**: Ensure Mecanum wheels form an 'X' pattern from the top.
* **Wiring**:
    * M1 (Front Left) -> Motor Terminal 1
    * M2 (Front Right) -> Motor Terminal 2
    * M3 (Back Left) -> Motor Terminal 3
    * M4 (Back Right) -> Motor Terminal 4

## Files

* `app.py`: Main Flask application and SocketIO logic.
* `motor_driver.py`: Motor driver class (handles Hardware or Mock).
* `test_motors.py`: Script to verify individual motor movement.
* `requirements.txt`: Python dependencies.
* `Makefile`: Shortcuts for common commands.
