import json
import os
import sys

from motor_driver import MotorDriver

CONFIG_FILE = "motor_config.json"

POSITIONS = [
    ("front_left", "Front-Left"),
    ("front_right", "Front-Right"),
    ("back_left", "Back-Left"),
    ("back_right", "Back-Right"),
]

DIRECTIONS = [
    ("forward", "Forward (Regular)", False),
    ("backward", "Backward (Inverted)", True),
]


def prompt_choice(prompt_text: str, num_options: int) -> int:
    """Prompts the user to select an integer option between 1 and num_options."""
    while True:
        try:
            choice_str = input(prompt_text).strip()
            if choice_str.isdigit():
                choice = int(choice_str)
                if 1 <= choice <= num_options:
                    return choice
            print(f"   [!] Invalid choice. Please enter a number between 1 and {num_options}.")
        except (KeyboardInterrupt, EOFError):
            print("\n   Aborted by user.")
            raise


def main():
    print("==================================================")
    print("        INTERACTIVE MOTOR MAPPING WIZARD          ")
    print("==================================================")
    print("This wizard will test each of the 4 motor channels (M1-M4).")
    print("For each channel, a motor will run at 50% power,")
    print("and you will specify which physical motor it is and")
    print("whether it is spinning forward or backward.")
    print("==================================================")

    # Check and consume force_mock.flag or sys.argv
    flag_path = "force_mock.flag"
    force_mock = False
    if "--mock" in sys.argv or "-m" in sys.argv:
        force_mock = True
        print("Forcing MOCK mode via command line flag.")
    elif os.path.exists(flag_path):
        try:
            os.remove(flag_path)
            force_mock = True
            print("Forcing MOCK mode from force_mock.flag.")
        except Exception as e:
            print(f"Failed to delete force_mock.flag ({e}). Ignoring mock flag.")

    driver = MotorDriver(mock=force_mock, config_path=CONFIG_FILE)

    channel_mapping = {}

    try:
        for ch in range(1, 5):
            print("\n--------------------------------------------------")
            print(f"STEP {ch}/4: Testing Motor Channel M{ch}")
            print("--------------------------------------------------")
            print(
                f" -> Spinning Motor Channel M{ch} at 50% throttle "
                "(will stay running until choices are submitted)..."
            )
            driver.drive_channel(ch, 0.5)

            # 1. Ask which motor position
            print(f"\nWhich motor was running on Channel M{ch}?")
            for idx, (_, display_name) in enumerate(POSITIONS, 1):
                print(f"  {idx}. {display_name}")

            pos_idx = prompt_choice(
                f"Select motor position [1-{len(POSITIONS)}]: ", len(POSITIONS)
            )
            pos_key, pos_display = POSITIONS[pos_idx - 1]

            # Re-assert motor spin to be 100% sure hardware PWM stays active
            driver.drive_channel(ch, 0.5)

            # 2. Ask direction (forward or backward)
            print(f"\nWas the {pos_display} motor running forward or backward?")
            for idx, (_, display_name, _) in enumerate(DIRECTIONS, 1):
                print(f"  {idx}. {display_name}")

            dir_idx = prompt_choice(
                f"Select direction [1-{len(DIRECTIONS)}]: ", len(DIRECTIONS)
            )
            dir_key, dir_display, is_inverted = DIRECTIONS[dir_idx - 1]

            # Stop channel only after both selections are made
            driver.drive_channel(ch, 0.0)
            print(f" -> Stopped Motor Channel M{ch}.")

            channel_mapping[str(ch)] = {
                "position": pos_key,
                "inverted": is_inverted,
                "label": pos_display,
                "direction": dir_key,
            }

            print(f"Recorded: Channel M{ch} => {pos_display} ({dir_display})")

        # Save to motor_config.json
        config_data = {"channels": channel_mapping}

        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=2)

        print("\n==================================================")
        print("          MOTOR MAPPING COMPLETE                  ")
        print("==================================================")
        print(f"Configuration saved to '{CONFIG_FILE}':\n")
        for ch_str, info in channel_mapping.items():
            dir_str = (
                "Backward (Inverted)" if info["inverted"] else "Forward (Regular)"
            )
            print(f"  Channel M{ch_str}: {info['label']:<12} | Direction: {dir_str}")
        print("==================================================")
        print("\nTo apply this configuration to a background app instance, run:")
        print("  sudo systemctl restart robot.service\n")

    except KeyboardInterrupt:
        print("\n\nMapping cancelled by user! Stopping all motors...")
    except Exception as e:
        print(f"\n\nAn error occurred during mapping: {e}")
    finally:
        try:
            driver.stop()
        except Exception:
            pass
        print("Motors safely stopped.")


if __name__ == "__main__":
    main()
