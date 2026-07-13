import os
import sys
import time

from gyro_driver import GyroDriver


def prompt_user(message):
    print(f"\n>>> {message}")
    input("    Press Enter to continue...")


def main():
    print("==================================================")
    print("           L3G4200D GYRO WIRING CHECK             ")
    print("==================================================")

    # Step 1: Wiring Instructions
    print("Please ensure your L3G4200D board is wired as follows:")
    print("--------------------------------------------------")
    print("  VIN  ->  3.3V (Pin 1) or 5V (Pin 2) - Check your board!")
    print("  GND  ->  Ground (Pin 6, 9, 14, 20, etc.)")
    print("  SDA  ->  SDA (GPIO 2, Pin 3)")
    print("  SCL  ->  SCL (GPIO 3, Pin 5)")
    print("  CS   ->  VIN (or Logic High) to enable I2C")
    print("  SDO  ->  GND (Address 0x68) or VIN (Address 0x69)")
    print("--------------------------------------------------")

    prompt_user("Verify wiring matches the above.")

    # Step 2: Initialization
    print("\nInitializing Gyro Driver...")

    # Check and consume force_mock.flag
    flag_path = "force_mock.flag"
    force_mock = False
    if os.path.exists(flag_path):
        try:
            os.remove(flag_path)
            force_mock = True
            print("Forcing MOCK mode for this check.")
        except Exception as e:
            print(f"Failed to delete force_mock.flag ({e}). Ignoring mock flag.")

    gyro = GyroDriver(mock=force_mock)

    if gyro.mock:
        print("\nWARNING: Driver is in MOCK mode.")
        print("This means the hardware was not detected or dependencies are missing.")
        print("We will simulate data for demonstration purposes.")
        prompt_user("Acknowledge MOCK mode.")
    else:
        print(f"SUCCESS: Gyro detected at address {hex(gyro.address)}.")

    # Step 3: Calibration
    print("\n--------------------------------------------------")
    print("STEP: Calibration")
    print("--------------------------------------------------")
    print("The sensor needs to measure its 'zero' state.")
    prompt_user("Place the robot on a stable surface and DO NOT MOVE IT.")

    gyro.calibrate(samples=200)

    # Step 4: Live Loop
    print("\n--------------------------------------------------")
    print("STEP: Live Data Stream")
    print("--------------------------------------------------")
    print("Press Ctrl+C to exit.")
    print("Columns:  X (deg/s)   |   Y (deg/s)   |   Z (deg/s)")
    print("--------------------------------------------------")

    try:
        while True:
            data = gyro.read_data()
            # Print with fixed width for readability
            print(
                f"\rX: {data.x:8.2f}   |   Y: {data.y:8.2f}   |   Z: {data.z:8.2f}",
                end="",
            )
            sys.stdout.flush()
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
    finally:
        print("Exiting.")


if __name__ == "__main__":
    main()
