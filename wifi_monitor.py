import logging
import os
import time
from typing import Optional

from wifi_manager import WifiManager


def monitor_wifi_loop(
        check_interval: int = 30,  # Seconds between connection checks
        boot_wait: int = 15,  # Delay before initial boot connection check
        sleep_func=time.sleep,  # Non-blocking sleep function (e.g. SocketIO sleep)
        wifi_manager: Optional[WifiManager] = None,  # Shared WifiManager instance
):
    """
    Background loop to ensure Wi-Fi connectivity.

    1. Checks for one-time force_hotspot.flag to boot directly into hotspot.
    2. Waits `boot_wait` seconds on startup (if not forcing hotspot) to let OS auto-connect.
    3. Checks connection.
    4. If disconnected, triggers Hotspot.
    5. Repeats check every `check_interval`.
    """
    wm = wifi_manager or WifiManager()
    logger = logging.getLogger("wifi_monitor")
    logging.basicConfig(level=logging.INFO)

    flag_path = "force_hotspot.flag"
    force_hotspot = False

    # 1. Verify we can write to the log output. If not, SKIP the flag to avoid lockout.
    log_writable = False
    try:
        with open("hotspot.log", "a") as lf:
            lf.write(f"\n--- Boot check: {time.asctime()} ---\n")
        log_writable = True
    except Exception as e:
        print(f"WifiMonitor: hotspot.log is not writable ({e}). Skipping force-hotspot checks to prevent lockout.")

    if log_writable:
        # Configure file logging since we verified it works
        try:
            file_handler = logging.FileHandler("hotspot.log")
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"WifiMonitor: Failed to add FileHandler: {e}")

        # 2. Check and consume the force-hotspot flag
        if os.path.exists(flag_path):
            try:
                # Attempt to delete the flag file.
                # If we can delete it now, it is gone and won't lock us out on the next boot.
                os.remove(flag_path)
                force_hotspot = True
                logger.warning("WifiMonitor: Successfully consumed force_hotspot.flag. Forcing hotspot mode.")
            except Exception as e:
                # If we cannot delete it, we skip the flag completely to prevent a lockout loop.
                logger.error(
                    f"WifiMonitor: Failed to delete force_hotspot.flag ({e}). Ignoring flag to prevent lockout.")

    if force_hotspot:
        logger.info("WifiMonitor: Skipping boot wait and forcing hotspot activation immediately...")
        wm.ensure_hotspot()
    else:
        logger.info(f"WifiMonitor: Starting... waiting {boot_wait}s for auto-connect.")
        # Allow initial boot phase for auto-connection
        sleep_func(boot_wait)

    while True:
        try:
            # Query the manager for connection details
            status = wm.get_status()

            if status["connected"]:
                logger.debug(
                    f"WifiMonitor: Connected to {status['ssid']} ({status['mode']}) at {status['ip']}"
                )
            else:
                logger.warning(
                    "WifiMonitor: Disconnected! Activating Hotspot fallback..."
                )
                # Fallback to local access point mode
                wm.ensure_hotspot()

        except Exception as e:
            logger.error(f"WifiMonitor: Error checking status: {e}")

        # Sleep before next connection check
        sleep_func(check_interval)


if __name__ == "__main__":
    # Script entrypoint for standalone monitoring
    monitor_wifi_loop()
