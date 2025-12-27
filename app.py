import math
# Add this import at the very top of app.py
from adafruit_motorkit import MotorKit
from flask import Flask, render_template
from flask_socketio import SocketIO


# Replace the previous 'class MotorDriver' with this:
class MotorDriver:
    def __init__(self):
        try:
            # The Adafruit Bonnet usually lives at address 0x60
            self.kit = MotorKit()
            print("Adafruit Motor Bonnet Connected!")
        except ValueError:
            print("ERROR: Motor Bonnet not found. Check I2C is enabled and battery is connected!")

    def drive(self, fl, fr, bl, br):
        # The library expects values between -1.0 and 1.0

        # M1 = Front Left
        self.kit.motor1.throttle = fl

        # M2 = Front Right
        self.kit.motor2.throttle = fr

        # M3 = Back Left
        self.kit.motor3.throttle = bl

        # M4 = Back Right
        self.kit.motor4.throttle = br


app = Flask(__name__)
# key for security, not critical for LAN but required by Flask
app.config['SECRET_KEY'] = 'robot_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- GLOBAL STATE ---
# Stores the robot's current compass heading from the Pixel 4
robot_heading = 0.0
motors = MotorDriver()


# --- ROUTES ---
@app.route('/controller')
def controller():
    return render_template('controller.html')


@app.route('/sensor')
def sensor():
    return render_template('sensor.html')


# --- WEBSOCKET LISTENERS ---

@socketio.on('sensor_data')
def handle_sensor(data):
    global robot_heading
    # Get heading (0-360) from Pixel 4
    # Note: Android 'alpha' is 0=North, increasing counter-clockwise usually
    robot_heading = float(data.get('heading', 0))


@socketio.on('joystick_data')
def handle_joystick(data):
    global robot_heading

    # 1. READ INPUTS
    # Left stick (Movement)
    lx = data.get('lx', 0)
    ly = data.get('ly', 0)  # Up should be positive

    # Right stick (Rotation)
    rx = data.get('rx', 0)  # Right should be positive

    # 2. FIELD-CENTRIC MATH
    # Convert degrees to radians
    theta = math.radians(robot_heading)

    # Rotate the vector
    # We counteract the robot's rotation to keep inputs "Field Aligned"
    # Note: You might need to swap +/- depending on if your compass goes CW or CCW
    field_x = lx * math.cos(theta) - ly * math.sin(theta)
    field_y = lx * math.sin(theta) + ly * math.cos(theta)

    # 3. MECANUM MIXING
    # Basic Mecanum Kinematics
    front_left = field_y + field_x + rx
    front_right = field_y - field_x - rx
    back_left = field_y - field_x + rx
    back_right = field_y + field_x - rx

    # 4. NORMALIZE (Keep proportions if we exceed speed limit)
    maximum = max(abs(front_left), abs(front_right), abs(back_left), abs(back_right), 1.0)
    front_left /= maximum
    front_right /= maximum
    back_left /= maximum
    back_right /= maximum

    # 5. EXECUTE
    motors.drive(front_left, front_right, back_left, back_right)


if __name__ == '__main__':
    # Host 0.0.0.0 makes it accessible on the LAN
    # SSL context is 'adhoc' to generate a quick self-signed cert for HTTPS
    socketio.run(app, host='0.0.0.0', port=5000, ssl_context='adhoc')
