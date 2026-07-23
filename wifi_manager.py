import logging
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Tuple

logger = logging.getLogger("wifi_manager")


@dataclass
class WifiNetwork:
    """Represents a scanned Wi-Fi network's details."""

    ssid: str  # Network name (SSID identifier)
    signal: int  # Signal strength percentage (0-100)
    security: str  # Encryption type (e.g., WPA2)


class WifiManager:
    """Handles network connections using NetworkManager CLI."""

    def __init__(self, mock: bool = False):
        self.nmcli_path = shutil.which("nmcli")
        self.is_mock = mock
        if self.is_mock:
            logger.info("WifiManager: Running in MOCK mode.")
            self._mock_state = {
                "connected": False,
                "ssid": None,
                "ip": "127.0.0.1",
                "mode": None,
            }
            return

        if self.nmcli_path is None:
            raise RuntimeError("nmcli not found. Configure force_mock.flag to run in mock mode.")

    def _run_command(self, args: List[str]) -> Tuple[bool, str]:
        """Executes nmcli command via subprocess. Returns (success, output)."""
        if self.is_mock:
            return True, ""

        try:
            # -t for terse, -f for fields
            cmd = [self.nmcli_path] + args
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return (result.returncode == 0), result.stdout.strip()
        except Exception as e:
            logger.error(f"WifiManager Error: {e}")
            return False, str(e)

    def _get_wifi_interface(self) -> str:
        """Finds the primary Wi-Fi device name (e.g. wlan0)."""
        if self.is_mock:
            return "wlan0"
        success, output = self._run_command(["-t", "-f", "DEVICE,TYPE", "dev"])
        if success and output:
            for line in output.split("\n"):
                parts = line.split(":")
                if len(parts) >= 2 and parts[1] == "wifi":
                    return parts[0]
        return "wlan0"

    def get_status(self) -> dict:
        """Retrieves current connection status, IP, and mode."""
        if self.is_mock:
            return {
                "connected": self._mock_state["connected"],
                "ssid": self._mock_state["ssid"],
                "ip": self._mock_state["ip"],
                "mode": self._mock_state["mode"],
            }

        # Check active connection
        # nmcli -t -f NAME,TYPE,DEVICE connection show --active
        success, output = self._run_command(
            ["-t", "-f", "NAME,TYPE,DEVICE", "connection", "show", "--active"]
        )

        state = {"connected": False, "ssid": None, "ip": None, "mode": "disconnected"}

        if success and output:
            # Expected: SSID:802-11-wireless:wlan0
            for line in output.split("\n"):
                parts = line.split(":")
                if len(parts) >= 2 and "wireless" in parts[1]:
                    state["ssid"] = parts[0]
                    state["connected"] = True
                    # Check if it is our Hotspot
                    if state["ssid"] == "RobotHotspot":
                        state["mode"] = "hotspot"
                    else:
                        state["mode"] = "client"
                    break

        # Get IP
        if state["connected"]:
            # ip -4 -o addr show wlan0
            # Simpler via nmcli: nmcli -t -f IP4.ADDRESS dev show wlan0
            # But device name might vary. Assuming wlan0 for Pi Zero 2 W usually.
            # Let's try getting it generically from hostname -I or socket,
            # but nmcli is consistent if we know the device.
            # Let's rely on app.py's get_local_ip() usually, but here:
            s_ok, s_out = self._run_command(["-t", "-f", "IP4.ADDRESS", "dev", "show"])
            if s_ok and s_out:
                # Output might contain multiple lines for multiple devices
                # IP4.ADDRESS[1]:192.168.1.100/24
                for line in s_out.split("\n"):
                    if "127.0.0.1" not in line and ":" in line:
                        # Format is usually IP4.ADDRESS[1]:192.168.x.x/24
                        ip_part = line.split(":", 1)[1]
                        state["ip"] = ip_part.split("/")[0]
                        break

        return state

    def scan_networks(self) -> List[WifiNetwork]:
        """Scans for available Wi-Fi networks in range."""
        if self.is_mock:
            return [
                WifiNetwork("Home-WiFi", 80, "WPA2"),
                WifiNetwork("Office-Guest", 60, "Open"),
                WifiNetwork("My-iPhone", 90, "WPA3"),
            ]

        # nmcli -t -f SSID,SIGNAL,SECURITY dev wifi list
        success, output = self._run_command(
            [
                "-t",
                "-f",
                "SSID,SIGNAL,SECURITY",
                "dev",
                "wifi",
                "list",
                "--rescan",
                "yes",
            ]
        )

        networks = []
        seen_ssids = set()

        if success and output:
            for line in output.split("\n"):
                # nmcli escapes colons with backslash, but -t usually separates fields by :
                # If SSID has ':', it is escaped like '\:'.
                # Simplification: split by unescaped colon is hard without regex.
                # However, usually SSID is first.
                # Let's rely on basic split for now, robust enough for most.
                parts = line.split(":")
                if len(parts) >= 3:
                    # Reconstruct SSID if it contained colons (naive approach, but acceptable for MVP)
                    # Actually, last two fields are SIGNAL and SECURITY.
                    security = parts[-1]
                    signal = parts[-2]
                    ssid = ":".join(parts[:-2])

                    ssid = ssid.replace(r"\:", ":")  # Unescape

                    if not ssid or ssid in seen_ssids:
                        continue

                    seen_ssids.add(ssid)
                    try:
                        sig_int = int(signal)
                    except ValueError:
                        sig_int = 0

                    networks.append(WifiNetwork(ssid, sig_int, security))

        # Sort by signal
        networks.sort(key=lambda x: x.signal, reverse=True)
        return networks

    def connect_to(self, ssid: str, password: str) -> Tuple[bool, str]:
        """Connects robot to a specific client Wi-Fi network."""
        logger.info(f"Attempting to connect to SSID: {ssid}")
        if self.is_mock:
            self._mock_state["connected"] = True
            self._mock_state["ssid"] = ssid
            self._mock_state["mode"] = "client"
            self._mock_state["ip"] = "192.168.1.150"
            logger.info(f"Connection successful (Mock Mode) to SSID: {ssid}")
            return True, "Mock connection successful"

        # nmcli dev wifi connect <SSID> password <PASSWORD>
        # Note: If open, password arg might cause error?
        # nmcli handles it usually, or we omit password arg.

        cmd = ["dev", "wifi", "connect", ssid]
        if password:
            cmd.extend(["password", password])

        success, output = self._run_command(cmd)
        if success:
            logger.info(f"Successfully connected to SSID: {ssid}")
        else:
            logger.error(f"Failed to connect to SSID: {ssid}. Output: {output}")
        return success, output

    def ensure_hotspot(self) -> bool:
        """
        Fallback mechanism to launch local Access Point.
        If connected to client Wi-Fi, does nothing.
        If offline, activates RobotHotspot so user can connect.
        """
        status = self.get_status()
        if status["connected"]:
            return True

        if self.is_mock:
            self._mock_state["mode"] = "hotspot"
            self._mock_state["ssid"] = "RobotHotspot"
            self._mock_state["connected"] = True
            self._mock_state["ip"] = "10.42.0.1"
            logger.warning("Mock: Activated Hotspot")
            return True

        logger.warning("WifiManager: Disconnected. Activating Hotspot...")

        # Check if connection profile exists
        # nmcli con show RobotHotspot
        exists, _ = self._run_command(["con", "show", "RobotHotspot"])

        if not exists:
            iface = self._get_wifi_interface()
            logger.info(f"WifiManager: Creating RobotHotspot profile on interface {iface}...")
            self._run_command(
                [
                    "con",
                    "add",
                    "type",
                    "wifi",
                    "ifname",
                    iface,
                    "con-name",
                    "RobotHotspot",
                    "autoconnect",
                    "yes",
                    "ssid",
                    "RobotHotspot",
                ]
            )
            self._run_command(
                [
                    "con",
                    "modify",
                    "RobotHotspot",
                    "802-11-wireless.mode",
                    "ap",
                    "802-11-wireless.band",
                    "bg",
                    "ipv4.method",
                    "shared",
                ]
            )

        # Activate it
        success, output = self._run_command(["con", "up", "RobotHotspot"])
        if success:
            logger.warning("WifiManager: Hotspot activated.")
        else:
            logger.error(f"WifiManager: Failed to activate hotspot: {output}")

        return success
