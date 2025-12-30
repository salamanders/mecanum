try:
    from adafruit_motorkit import MotorKit
except ImportError:
    MotorKit = None


class MotorDriver:
    def __init__(self):
        self.mock = False
        self.kit = None

        if MotorKit:
            try:
                # The Adafruit Bonnet usually lives at address 0x60
                self.kit = MotorKit()
                print("Adafruit Motor Bonnet Connected!")
            except ValueError:
                print(
                    "ERROR: Motor Bonnet not found. Check I2C is enabled and battery is connected!"
                )
                print("Falling back to MOCK mode.")
                self.mock = True
            except Exception as e:
                print(f"ERROR: Failed to initialize MotorKit: {e}")
                print("Falling back to MOCK mode.")
                self.mock = True
        else:
            print("adafruit-circuitpython-motorkit not installed.")
            print("Falling back to MOCK mode.")
            self.mock = True

    def drive(self, fl, fr, bl, br):
        """
        Drives the motors.
        fl, fr, bl, br: Throttle values between -1.0 and 1.0
        """
        if self.mock:
            print(f"MOCK DRIVE: FL={fl:.2f}, FR={fr:.2f}, BL={bl:.2f}, BR={br:.2f}")
            return

        # The library expects values between -1.0 and 1.0
        # M1 = Front Left
        self.kit.motor1.throttle = fl

        # M2 = Front Right
        self.kit.motor2.throttle = fr

        # M3 = Back Left
        self.kit.motor3.throttle = bl

        # M4 = Back Right
        self.kit.motor4.throttle = br
