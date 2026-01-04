import math
import socket
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from motor_driver import MotorDriver


app = Flask(__name__)
# key for security, not critical for LAN but required by Flask
app.config["SECRET_KEY"] = "robot_secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# --- GLOBAL STATE ---
# Stores the robot's current compass heading from the Pixel 4
robot_heading = 0.0
# Stores the robot's linear acceleration (x, y, z)
robot_accel = {"x": 0.0, "y": 0.0, "z": 0.0}
motors = MotorDriver()


def get_ip_address():
    """Finds the local IP address of the device."""
    try:
        # Connect to a public DNS server (doesn't actually send data)
        # to determine the outgoing interface IP.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# --- ROUTES ---
@app.route("/controller")
def controller():
    return render_template("controller.html")


@app.route("/sensor")
def sensor():
    return render_template("sensor.html")


# --- WEBSOCKET LISTENERS ---


@socketio.on("connect")
def handle_connect():
    """Sent when a client connects."""
    ip = get_ip_address()
    controller_url = f"https://{ip}:5000/controller"
    # Send robot info back to the client
    # We broadcast or emit to the specific client. Here we just emit to the sender.
    emit(
        "robot_info",
        {
            "controller_url": controller_url,
            "battery_level": None,  # Placeholder for future battery hardware
        },
    )


@socketio.on("sensor_data")
def handle_sensor(data):
    global robot_heading, robot_accel
    # Get heading (0-360) from Pixel 4
    # Note: Android 'alpha' is 0=North, increasing counter-clockwise usually
    robot_heading = float(data.get("heading", 0))

    # Get acceleration (linear, excluding gravity)
    accel = data.get("accel", {})
    robot_accel["x"] = float(accel.get("x", 0))
    robot_accel["y"] = float(accel.get("y", 0))
    robot_accel["z"] = float(accel.get("z", 0))


@socketio.on("joystick_data")
def handle_joystick(data):
    global robot_heading

    # 1. READ INPUTS
    # Left stick (Movement)
    lx = data.get("lx", 0)
    ly = data.get("ly", 0)  # Up should be positive

    # Right stick (Rotation)
    rx = data.get("rx", 0)  # Right should be positive

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
    maximum = max(
        abs(front_left), abs(front_right), abs(back_left), abs(back_right), 1.0
    )
    front_left /= maximum
    front_right /= maximum
    back_left /= maximum
    back_right /= maximum

    # 5. EXECUTE
    motors.drive(front_left, front_right, back_left, back_right)


if __name__ == "__main__":
    # Host 0.0.0.0 makes it accessible on the LAN
    # SSL context is 'adhoc' to generate a quick self-signed cert for HTTPS
    # socketio.run(app, host='0.0.0.0', port=5000, ssl_context='adhoc')
    # Eventlet (used by flask_socketio) requires certfile/keyfile args, not ssl_context
    socketio.run(app, host="0.0.0.0", port=5000, certfile="cert.pem", keyfile="key.pem")
