import math
import socket
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from motor_driver import MotorDriver


app = Flask(__name__)
# key for security, not critical for LAN but required by Flask
app.config["SECRET_KEY"] = "robot_secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# --- GLOBAL STATE ---
# Stores the robot's current compass heading from the Pixel 4
robot_heading = 0.0
# Stores the robot's current acceleration (unused by motors, but logged/stored)
robot_accel = {"ax": 0, "ay": 0, "az": 0}

motors = MotorDriver()


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("8.8.8.8", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def send_status_update(target_sid=None):
    ip = get_local_ip()
    # Construct the Controller URL
    url = f"https://{ip}:5000/controller"

    data = {
        "url": url,
        "battery": None,  # Placeholder for battery level
    }

    if target_sid:
        socketio.emit("robot_status", data, room=target_sid)
    else:
        socketio.emit("robot_status", data)  # Broadcast


def background_status_task():
    """Background task to send status updates every 60 seconds."""
    while True:
        socketio.sleep(60)
        send_status_update()


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
    # Send status immediately upon connection
    send_status_update(request.sid)


@socketio.on("sensor_data")
def handle_sensor(data):
    global robot_heading, robot_accel
    # Get heading (0-360) from Pixel 4
    # Note: Android 'alpha' is 0=North, increasing counter-clockwise usually
    robot_heading = float(data.get("heading", 0))

    # Store acceleration data
    robot_accel["ax"] = float(data.get("ax", 0))
    robot_accel["ay"] = float(data.get("ay", 0))
    robot_accel["az"] = float(data.get("az", 0))


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
    # Start background task
    socketio.start_background_task(background_status_task)

    # Host 0.0.0.0 makes it accessible on the LAN
    # SSL context is 'adhoc' to generate a quick self-signed cert for HTTPS
    # socketio.run(app, host='0.0.0.0', port=5000, ssl_context='adhoc')
    socketio.run(app, host="0.0.0.0", port=5000, certfile="cert.pem", keyfile="key.pem")
