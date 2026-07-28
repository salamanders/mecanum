import json
import os
from dataclasses import dataclass
from typing import Dict, Optional, Protocol, Any

# Type Alias for clarity
ThrottleValue = float


class MotorKitProtocol(Protocol):
    """Protocol for the MotorKit object to support Mocking cleanly."""

    class Motor(Protocol):
        throttle: Optional[ThrottleValue]

    motor1: Motor
    motor2: Motor
    motor3: Motor
    motor4: Motor


@dataclass
class MotorSpeeds:
    """Represents the throttle values for the 4 mecanum wheels."""

    front_left: float
    front_right: float
    back_left: float
    back_right: float


# Default mapping if motor_config.json does not exist
DEFAULT_MOTOR_CONFIG: Dict[str, Dict[str, Any]] = {
    "1": {"position": "front_left", "inverted": False},
    "2": {"position": "front_right", "inverted": False},
    "3": {"position": "back_left", "inverted": False},
    "4": {"position": "back_right", "inverted": False},
}


class MotorDriver:
    """
    Handles motor control.
    Supports motor mapping & inversion configuration via motor_config.json.
    Automatically falls back to a Mock implementation if hardware is missing.
    """

    def __init__(self, mock: bool = False, config_path: str = "motor_config.json") -> None:
        self.mock: bool = mock
        self.config_path: str = config_path
        self.config: Dict[str, Dict[str, Any]] = self.load_config(config_path)
        self.kit: Optional[MotorKitProtocol] = None

        if self.mock:
            print("MotorDriver: Running in MOCK mode.")
            return

        from adafruit_motorkit import MotorKit

        # The Adafruit Bonnet usually lives at address 0x60
        self.kit = MotorKit()
        print("Adafruit Motor Bonnet Connected!")

    def load_config(self, path: str) -> Dict[str, Dict[str, Any]]:
        """Loads motor mapping configuration from file or falls back to default."""
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    if "channels" in data and isinstance(data["channels"], dict):
                        print(f"MotorDriver: Loaded motor mapping config from {path}")
                        return data["channels"]
                    elif isinstance(data, dict):
                        print(f"MotorDriver: Loaded motor mapping config from {path}")
                        return data
            except Exception as e:
                print(f"MotorDriver: Failed to load config from {path} ({e}). Using defaults.")
        return DEFAULT_MOTOR_CONFIG.copy()

    def drive_channel(self, channel: int, throttle: float) -> None:
        """
        Drives a raw motor channel (1-4) directly at the specified throttle (-1.0 to 1.0).
        """
        def _clamp(val: float) -> float:
            return max(-1.0, min(1.0, val))

        clamped = _clamp(throttle)

        if self.mock or self.kit is None:
            print(f"MOCK DRIVE CHANNEL {channel}: throttle={clamped:.2f}")
            return

        if channel == 1:
            self.kit.motor1.throttle = clamped
        elif channel == 2:
            self.kit.motor2.throttle = clamped
        elif channel == 3:
            self.kit.motor3.throttle = clamped
        elif channel == 4:
            self.kit.motor4.throttle = clamped

    def stop(self) -> None:
        """Stops all motors on all channels."""
        self.drive_channel(1, 0.0)
        self.drive_channel(2, 0.0)
        self.drive_channel(3, 0.0)
        self.drive_channel(4, 0.0)

    def drive(self, speeds: MotorSpeeds) -> None:
        """
        Drives the motors using the provided MotorSpeeds dataclass,
        mapped according to channel configuration and inversion settings.
        """
        def _clamp(val: float) -> float:
            return max(-1.0, min(1.0, val))

        speed_map = {
            "front_left": speeds.front_left,
            "front_right": speeds.front_right,
            "back_left": speeds.back_left,
            "back_right": speeds.back_right,
        }

        # Calculate throttle for each channel 1..4 based on config
        channel_throttles: Dict[int, float] = {}
        for ch in (1, 2, 3, 4):
            ch_key = str(ch)
            ch_cfg = self.config.get(ch_key, DEFAULT_MOTOR_CONFIG.get(ch_key, {}))
            position = ch_cfg.get("position", "front_left")
            inverted = ch_cfg.get("inverted", False)

            target_speed = speed_map.get(position, 0.0)
            throttled_speed = -target_speed if inverted else target_speed
            channel_throttles[ch] = _clamp(throttled_speed)

        if self.mock or self.kit is None:
            print(
                f"MOCK DRIVE: CH1({self.config.get('1', {}).get('position', 'fl')})={channel_throttles[1]:.2f}, "
                f"CH2({self.config.get('2', {}).get('position', 'fr')})={channel_throttles[2]:.2f}, "
                f"CH3({self.config.get('3', {}).get('position', 'bl')})={channel_throttles[3]:.2f}, "
                f"CH4({self.config.get('4', {}).get('position', 'br')})={channel_throttles[4]:.2f}"
            )
            return

        self.kit.motor1.throttle = channel_throttles[1]
        self.kit.motor2.throttle = channel_throttles[2]
        self.kit.motor3.throttle = channel_throttles[3]
        self.kit.motor4.throttle = channel_throttles[4]
