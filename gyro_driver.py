import random
import time
from dataclasses import dataclass
from typing import Optional

# Register Constants
L3G4200D_WHO_AM_I = 0x0F
L3G4200D_CTRL_REG1 = 0x20
L3G4200D_CTRL_REG2 = 0x21
L3G4200D_CTRL_REG3 = 0x22
L3G4200D_CTRL_REG4 = 0x23
L3G4200D_CTRL_REG5 = 0x24
L3G4200D_OUT_X_L = 0x28
L3G4200D_STATUS_REG = 0x27

# I2C Addresses
L3G4200D_ADDRESS_68 = 0x68
L3G4200D_ADDRESS_69 = 0x69
L3G4200D_ID = 0xD3


@dataclass
class GyroData:
    """Represents the angular velocity in degrees per second."""

    x: float
    y: float
    z: float


class GyroDriver:
    """
    Driver for L3G4200D 3-axis Gyroscope.
    Handles I2C communication, configuration, and data reading.
    Falls back to Mock mode if hardware is missing.
    """

    def __init__(self, mock: bool = False) -> None:
        self.mock: bool = mock
        self.i2c = None
        self.address: Optional[int] = None
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.offset_z: float = 0.0

        if self.mock:
            print("Gyro Driver: Running in MOCK mode.")
            return

        import board
        import busio

        # Initialize I2C
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Scan for device
        while not self.i2c.try_lock():
            pass

        try:
            addresses = self.i2c.scan()
            print(f"I2C Scan found: {[hex(a) for a in addresses]}")

            if L3G4200D_ADDRESS_69 in addresses:
                self.address = L3G4200D_ADDRESS_69
            elif L3G4200D_ADDRESS_68 in addresses:
                self.address = L3G4200D_ADDRESS_68

            if self.address is None:
                raise OSError("L3G4200D not found on I2C bus.")

            # Verify ID
            # Write to WHO_AM_I register (0x0F)
            self._write_register(
                L3G4200D_WHO_AM_I, []
            )

            # Check WHO_AM_I
            chip_id = self._read_register(L3G4200D_WHO_AM_I)
            if chip_id != L3G4200D_ID:
                print(
                    f"Warning: Unexpected Chip ID: {hex(chip_id)} (Expected {hex(L3G4200D_ID)})"
                )

            # Initialize Configuration
            self._initialize_chip()
            print(f"L3G4200D initialized at address {hex(self.address)}")

        finally:
            self.i2c.unlock()

    def _write_register(self, register: int, value: int) -> None:
        """Writes a byte to a specific register. Assumes I2C lock is held."""
        if self.mock or not self.i2c or not self.address:
            return

        # busio.I2C expects a bytes-like object
        # We send [Register, Value]
        buffer = bytearray([register, value])
        self.i2c.writeto(self.address, buffer)

    def _read_register(self, register: int) -> int:
        """Reads a single byte from a register. Assumes I2C lock is held."""
        if self.mock or not self.i2c or not self.address:
            return 0

        result = bytearray(1)
        self.i2c.writeto_then_readfrom(self.address, bytes([register]), result)
        return result[0]

    def _read_bytes(self, start_register: int, length: int) -> bytearray:
        """Reads multiple bytes starting from a register (asserting MSB for auto-increment). Assumes I2C lock is held."""
        if self.mock or not self.i2c or not self.address:
            return bytearray(length)

        # Set bit 7 (MSB) to 1 for auto-increment
        reg_addr = start_register | 0x80
        result = bytearray(length)
        self.i2c.writeto_then_readfrom(self.address, bytes([reg_addr]), result)
        return result

    def _initialize_chip(self) -> None:
        """Sets up the control registers. Assumes I2C lock is held."""
        # CTRL_REG1 (0x20):
        # DR1 DR0 BW1 BW0 PD Zen Yen Xen
        # 0   0   (100Hz)
        #         0   0   (Cut-off 12.5)
        #                 1   (Power ON)
        #                     1   1   1 (Enable Axes)
        # Binary: 0000 1111 -> 0x0F
        self._write_register(L3G4200D_CTRL_REG1, 0x0F)

        # CTRL_REG4 (0x23):
        # BDU BLE FS1 FS0 - ST1 ST0 SIM
        # 0   (Continuous update)
        #     0   (Little Endian)
        #         1   0   (2000 dps full scale)
        #                 0   0   0   0
        # Binary: 0010 0000 -> 0x20 No wait, FS=2000dps is FS1=1, FS0=0?
        # Datasheet: FS1-FS0: 00=250, 01=500, 10=2000, 11=2000
        # So 10 -> 0x30? No. Bit 5 and 4.
        # 7 6 5 4 3 2 1 0
        # BDU BLE FS1 FS0 - ST1 ST0 SIM
        # 0 0 1 1 0 0 0 0 -> 0x30 (2000 dps)
        self._write_register(L3G4200D_CTRL_REG4, 0x30)

    def calibrate(self, samples: int = 100) -> None:
        """
        Reads N samples to determine the zero-rate level (bias).
        Robot must be stationary.
        """
        if self.mock:
            print("MOCK Calibration: Done.")
            return

        print(f"Calibrating Gyro ({samples} samples)... DO NOT MOVE ROBOT.")
        sum_x, sum_y, sum_z = 0.0, 0.0, 0.0

        # Temporary disable offsets to read raw values
        old_ox, old_oy, old_oz = self.offset_x, self.offset_y, self.offset_z
        self.offset_x, self.offset_y, self.offset_z = 0.0, 0.0, 0.0

        try:
            for _ in range(samples):
                data = self.read_data()
                sum_x += data.x
                sum_y += data.y
                sum_z += data.z
                time.sleep(0.01)  # 10ms delay (100Hz ODR)

            self.offset_x = sum_x / samples
            self.offset_y = sum_y / samples
            self.offset_z = sum_z / samples

            print(
                f"Calibration Complete. Offsets: X={self.offset_x:.2f}, Y={self.offset_y:.2f}, Z={self.offset_z:.2f}"
            )

        except Exception as e:
            print(f"Calibration failed: {e}")
            # Restore old offsets if failed
            self.offset_x, self.offset_y, self.offset_z = old_ox, old_oy, old_oz

    def read_data(self) -> GyroData:
        """Reads the current angular velocity."""
        if self.mock:
            # Return some random noise
            return GyroData(
                x=random.uniform(-0.5, 0.5),
                y=random.uniform(-0.5, 0.5),
                z=random.uniform(-0.5, 0.5),
            )

        # Acquire lock correctly
        while not self.i2c.try_lock():
            pass

        try:
            # Read 6 bytes: XL, XH, YL, YH, ZL, ZH
            raw_bytes = self._read_bytes(L3G4200D_OUT_X_L, 6)
        finally:
            self.i2c.unlock()

        # Convert to 16-bit signed
        # struct.unpack('<hhh', raw_bytes) would be cleaner, but let's do it manually to avoid import if we can or just use struct
        import struct

        x, y, z = struct.unpack("<hhh", raw_bytes)

        # Scale Factor for 2000 dps is typically 70 mdps/digit (0.07 dps/digit)
        # Check datasheet. 2000dps -> 70 mdps/LSB
        sensitivity = 0.07

        gx = x * sensitivity - self.offset_x
        gy = y * sensitivity - self.offset_y
        gz = z * sensitivity - self.offset_z

        return GyroData(x=gx, y=gy, z=gz)
