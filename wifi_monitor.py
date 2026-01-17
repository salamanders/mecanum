import time
import logging
from wifi_manager import WifiManager


def monitor_wifi_loop(check_interval: int = 30, boot_wait: int = 15, sleep_func=time.sleep):
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
    sleep_func(boot_wait)

    while True:
        try:
            status = wm.get_status()

            if status["connected"]:
                logger.debug(
                    f"WifiMonitor: Connected to {status['ssid']} ({status['mode']}) at {status['ip']}"
                )
            else:
                logger.warning(
                    "WifiMonitor: Disconnected! Activating Hotspot fallback..."
                )
                wm.ensure_hotspot()

        except Exception as e:
            logger.error(f"WifiMonitor: Error checking status: {e}")

        sleep_func(check_interval)


if __name__ == "__main__":
    monitor_wifi_loop()
