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

    def __init__(self, mock: bool = False) -> None:
        self.mock: bool = mock
        self.kit: Optional[MotorKitProtocol] = None

        if self.mock:
            print("MotorDriver: Running in MOCK mode.")
            return

        from adafruit_motorkit import MotorKit

        # The Adafruit Bonnet usually lives at address 0x60
        self.kit = MotorKit()
        print("Adafruit Motor Bonnet Connected!")

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
        def _clamp(val: float) -> float:
            return max(-1.0, min(1.0, val))

        # M1 = Front Left
        self.kit.motor1.throttle = _clamp(speeds.front_left)

        # M2 = Front Right
        self.kit.motor2.throttle = _clamp(speeds.front_right)

        # M3 = Back Left
        self.kit.motor3.throttle = _clamp(speeds.back_left)

        # M4 = Back Right
        self.kit.motor4.throttle = _clamp(speeds.back_right)

