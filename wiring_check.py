from motor_driver import MotorDriver, MotorSpeeds


def prompt_user(message):
    print(f"\n>>> {message}")
    input("    Press Enter to continue...")


def main():
    print("Initializing Motor Driver...")
    driver = MotorDriver()

    # Motor configurations: (ID, Position, Drive Args)
    # Drive Args format: (fl, fr, bl, br)
    motors = [
        {"id": "M1", "pos": "Front-Left", "args": (0.5, 0, 0, 0)},
        {"id": "M2", "pos": "Front-Right", "args": (0, 0.5, 0, 0)},
        {"id": "M3", "pos": "Back-Left", "args": (0, 0, 0.5, 0)},
        {"id": "M4", "pos": "Back-Right", "args": (0, 0, 0, 0.5)},
    ]

    print("==================================================")
    print("           INTERACTIVE WIRING CHECK               ")
    print("==================================================")
    print("This wizard will guide you through verifying the wiring")
    print("for all 4 motors. Please have a multimeter ready.")
    print("==================================================")

    try:
        for motor in motors:
            mid = motor["id"]
            pos = motor["pos"]
            drive_args = motor["args"]

            print("\n--------------------------------------------------")
            print(f"STEP: Testing Motor {mid} ({pos})")
            print("--------------------------------------------------")

            # 1. Setup voltage check
            prompt_user(
                f"Connect multimeter leads to terminal block {mid}.\n    (Ensure no wheel is connected if possible, or wheel is safely elevated)"
            )

            print(f"    -> Powering {mid} at 50% throttle...")
            driver.drive(MotorSpeeds(*drive_args))

            # 2. Verify voltage
            prompt_user(
                f"Power is ON. Verify that at least +6V is present on pins {mid}.\n    (If voltage is negative, note that wires might be swapped, but check spin direction next)"
            )

            # 3. Connect wheel / Verify Spin
            print("    -> Keeping power ON...")
            prompt_user(
                f"Now connect the {pos} wheel (if not connected).\n    It should be spinning FORWARD.\n    If it is spinning BACKWARD, swap the wires for this motor!"
            )

            # 4. Stop
            print(f"    -> Stopping {mid}...")
            driver.drive(MotorSpeeds(0, 0, 0, 0))

            prompt_user(f"Test for {mid} ({pos}) complete.")

        print("\n==================================================")
        print("           ALL CHECKS COMPLETE                    ")
        print("==================================================")

    except KeyboardInterrupt:
        print("\n\nAborted by user! Stopping all motors...")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
    finally:
        # Ensure motors are stopped
        try:
            driver.drive(MotorSpeeds(0, 0, 0, 0))
        except Exception:
            pass
        print("Motors stopped. Exiting.")


if __name__ == "__main__":
    main()
