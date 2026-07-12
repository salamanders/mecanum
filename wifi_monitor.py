import logging
import time

from wifi_manager import WifiManager


def monitor_wifi_loop(
        check_interval: int = 30,  # Seconds between connection checks
        boot_wait: int = 15,  # Delay before initial boot connection check
        sleep_func=time.sleep,  # Non-blocking sleep function (e.g. SocketIO sleep)
):
    """
    Background loop to ensure Wi-Fi connectivity.

    1. Waits `boot_wait` seconds on startup to let OS auto-connect to known networks.
    2. Checks connection.
    3. If disconnected, triggers Hotspot.
    4. Repeats check every `check_interval`.
    """
    wm = WifiManager()
    logger = logging.getLogger("wifi_monitor")
    logging.basicConfig(level=logging.INFO)

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
