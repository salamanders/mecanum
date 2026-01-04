import math
import os
import socket
from dataclasses import dataclass
from typing import TypedDict, Optional, Dict, Any

from OpenSSL import crypto
from flask import Flask, render_template, request
from flask_socketio import SocketIO

from motor_driver import MotorDriver, MotorSpeeds


# --- TYPES & DATA CLASSES ---


@dataclass
class RobotState:
    """Stores the current state of the robot sensors."""

    heading: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    az: float = 0.0


@dataclass
class JoystickInput:
    """Represents the input from the twin-stick controller."""

    lx: float  # Left Stick X (Strafe)
    ly: float  # Left Stick Y (Drive)
    rx: float  # Right Stick X (Rotate)


class StatusData(TypedDict):
    """Type definition for the status update payload."""

    url: str
    battery: Optional[str]


# --- LOGIC HELPERS ---


def calculate_mecanum_speeds(
    input_data: JoystickInput, heading_degrees: float
) -> MotorSpeeds:
    """
    Calculates the motor speeds for a mecanum wheel robot with field-centric control.

    :param input_data: Joystick inputs (lx, ly, rx)
    :param heading_degrees: Current robot heading in degrees
    :return: MotorSpeeds object with normalized throttle values
    """
    # 1. Field-Centric Math
    # Convert degrees to radians
    theta = math.radians(heading_degrees)

    # Rotate the vector
    # We counteract the robot's rotation to keep inputs "Field Aligned"
    field_x = input_data.lx * math.cos(theta) - input_data.ly * math.sin(theta)
    field_y = input_data.lx * math.sin(theta) + input_data.ly * math.cos(theta)

    # 2. Mecanum Kinematics
    # front_left = y + x + rot
    front_left = field_y + field_x + input_data.rx
    front_right = field_y - field_x - input_data.rx
    back_left = field_y - field_x + input_data.rx
    back_right = field_y + field_x - input_data.rx

    # 3. Normalize
    # Ensure no value exceeds 1.0 while maintaining proportions
    maximum = max(
        abs(front_left), abs(front_right), abs(back_left), abs(back_right), 1.0
    )

    return MotorSpeeds(
        front_left=front_left / maximum,
        front_right=front_right / maximum,
        back_left=back_left / maximum,
        back_right=back_right / maximum,
    )


def get_local_ip() -> str:
    """Detects the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("8.8.8.8", 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "127.0.0.1"
    finally:
        s.close()
    return str(ip_address)


# --- FLASK SETUP ---

app = Flask(__name__)
# key for security, not critical for LAN but required by Flask
app.config["SECRET_KEY"] = "robot_secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# --- GLOBAL STATE ---

robot_state = RobotState()
motors = MotorDriver()


def send_status_update(target_sid: Optional[str] = None) -> None:
    """
    Broadcasts or sends a status update to a specific client.
    Includes the Controller URL and battery status.
    """
    ip = get_local_ip()
    url = f"https://{ip}:5000/controller"

    data: StatusData = {
        "url": url,
        "battery": None,  # Placeholder for battery level
    }

    if target_sid:
        socketio.emit("robot_status", data, room=target_sid)
    else:
        socketio.emit("robot_status", data)


def background_status_task() -> None:
    """Background task to send status updates every 60 seconds."""
    while True:
        socketio.sleep(60)
        send_status_update()


# --- ROUTES ---


@app.route("/controller")
def controller() -> str:
    return render_template("controller.html")


@app.route("/sensor")
def sensor() -> str:
    return render_template("sensor.html")


# --- WEBSOCKET LISTENERS ---


@socketio.on("connect")
def handle_connect() -> None:
    # Send status immediately upon connection
    send_status_update(request.sid)


@socketio.on("sensor_data")
def handle_sensor(data: Dict[str, Any]) -> None:
    """
    Receives sensor data from the phone/client.
    Expected data: heading, ax, ay, az
    """
    # Note: Android 'alpha' is 0=North, increasing counter-clockwise usually
    robot_state.heading = float(data.get("heading", 0))
    robot_state.ax = float(data.get("ax", 0))
    robot_state.ay = float(data.get("ay", 0))
    robot_state.az = float(data.get("az", 0))


@socketio.on("joystick_data")
def handle_joystick(data: Dict[str, Any]) -> None:
    """
    Receives joystick input and drives the motors.
    Expected data: lx, ly, rx
    """
    # 1. Parse Input (with defaults)
    input_data = JoystickInput(
        lx=float(data.get("lx", 0)),
        ly=float(data.get("ly", 0)),  # Up should be positive
        rx=float(data.get("rx", 0)),  # Right should be positive
    )

    # 2. Calculate Speeds
    speeds = calculate_mecanum_speeds(input_data, robot_state.heading)

    # 3. Execute
    motors.drive(speeds)


def ensure_certificates() -> None:
    """
    Generates self-signed 'cert.pem' and 'key.pem' if they do not exist.
    This ensures HTTPS works out-of-the-box for DeviceOrientation API support.
    """
    cert_file = "cert.pem"
    key_file = "key.pem"

    if os.path.exists(cert_file) and os.path.exists(key_file):
        return

    print("Generating self-signed certificates for HTTPS...")
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    cert = crypto.X509()
    cert.get_subject().C = "US"
    cert.get_subject().ST = "RobotState"
    cert.get_subject().L = "RobotCity"
    cert.get_subject().O = "Robot"
    cert.get_subject().OU = "RobotUnit"
    cert.get_subject().CN = "robot.local"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, "sha256")

    with open(cert_file, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(key_file, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
    print(f"Certificates generated: {cert_file}, {key_file}")


if __name__ == "__main__":
    # Ensure SSL certs exist (required for modern browser sensors)
    ensure_certificates()

    # Start background task
    socketio.start_background_task(background_status_task)

    # Host 0.0.0.0 makes it accessible on the LAN
    socketio.run(app, host="0.0.0.0", port=5000, certfile="cert.pem", keyfile="key.pem")
