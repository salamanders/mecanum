from dataclasses import dataclass
from typing import Optional, Protocol

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


class MotorDriver:
    """
    Handles motor control.
    Automatically falls back to a Mock implementation if hardware is missing.
    """

    def __init__(self) -> None:
        self.mock: bool = False
        self.kit: Optional[MotorKitProtocol] = None

        try:
            from adafruit_motorkit import MotorKit

            # The Adafruit Bonnet usually lives at address 0x60
            self.kit = MotorKit()
            print("Adafruit Motor Bonnet Connected!")

        except ImportError as e:
            print(f"adafruit-circuitpython-motorkit import failed: {e}")
            print("Falling back to MOCK mode.")
            self.mock = True

        except (ValueError, OSError) as e:
            # ValueError often happens if I2C is not enabled or device not found
            print(f"ERROR: Motor Bonnet hardware error: {e}")
            print("Falling back to MOCK mode.")
            self.mock = True

        except Exception as e:
            print(f"ERROR: Unexpected initialization error: {e}")
            print("Falling back to MOCK mode.")
            self.mock = True

    def drive(self, speeds: MotorSpeeds) -> None:
        """
        Drives the motors using the provided MotorSpeeds dataclass.
        """
        if self.mock or self.kit is None:
            print(
                f"MOCK DRIVE: FL={speeds.front_left:.2f}, FR={speeds.front_right:.2f}, "
                f"BL={speeds.back_left:.2f}, BR={speeds.back_right:.2f}"
            )
            return

        # The library expects values between -1.0 and 1.0
        # M1 = Front Left
        self.kit.motor1.throttle = speeds.front_left

        # M2 = Front Right
        self.kit.motor2.throttle = speeds.front_right

        # M3 = Back Left
        self.kit.motor3.throttle = speeds.back_left

        # M4 = Back Right
        self.kit.motor4.throttle = speeds.back_right
