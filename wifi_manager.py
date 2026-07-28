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
        # mock parameter accepted for backwards compatibility
        self.nmcli_path = shutil.which("nmcli")

    def _run_command(self, args: List[str]) -> Tuple[bool, str]:
        """Executes nmcli command via subprocess. Returns (success, output)."""
        if self.nmcli_path is None:
            return False, "nmcli not installed on this system"

        try:
            cmd = [self.nmcli_path] + args
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return (result.returncode == 0), result.stdout.strip()
        except Exception as e:
            logger.error(f"WifiManager Error: {e}")
            return False, str(e)

    def _get_wifi_interface(self) -> str:
        """Finds the primary Wi-Fi device name (e.g. wlan0)."""
        success, output = self._run_command(["-t", "-f", "DEVICE,TYPE", "dev"])
        if success and output:
            for line in output.split("\n"):
                parts = line.split(":")
                if len(parts) >= 2 and parts[1] == "wifi":
                    return parts[0]
        return "wlan0"

    def get_status(self) -> dict:
        """Retrieves current connection status, IP, and mode."""
        state = {"connected": False, "ssid": None, "ip": None, "mode": "disconnected"}

        success, output = self._run_command(
            ["-t", "-f", "NAME,TYPE,DEVICE", "connection", "show", "--active"]
        )

        if success and output:
            for line in output.split("\n"):
                parts = line.split(":")
                if len(parts) >= 2 and ("wireless" in parts[1] or parts[1] == "wifi"):
                    state["ssid"] = parts[0]
                    state["connected"] = True
                    state["mode"] = (
                        "hotspot" if state["ssid"] == "RobotHotspot" else "client"
                    )
                    break

        if state["connected"]:
            iface = self._get_wifi_interface()
            s_ok, s_out = self._run_command(
                ["-t", "-f", "IP4.ADDRESS", "dev", "show", iface]
            )
            if s_ok and s_out:
                for line in s_out.split("\n"):
                    if ":" in line:
                        ip_part = line.split(":", 1)[1]
                        state["ip"] = ip_part.split("/")[0]
                        break

        return state

    def scan_networks(self) -> List[WifiNetwork]:
        """Scans for available Wi-Fi networks in range."""
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
                parts = line.split(":")
                if len(parts) >= 3:
                    security = parts[-1]
                    signal = parts[-2]
                    ssid = ":".join(parts[:-2]).replace(r"\:", ":")

                    if not ssid or ssid in seen_ssids:
                        continue

                    seen_ssids.add(ssid)
                    try:
                        sig_int = int(signal)
                    except ValueError:
                        sig_int = 0

                    networks.append(WifiNetwork(ssid, sig_int, security))

        networks.sort(key=lambda x: x.signal, reverse=True)
        return networks

    def connect_to(self, ssid: str, password: str) -> Tuple[bool, str]:
        """Connects robot to a specific client Wi-Fi network."""
        logger.info(f"Attempting to connect to SSID: {ssid}")
        cmd = ["dev", "wifi", "connect", ssid]
        if password:
            cmd.extend(["password", password])

        success, output = self._run_command(cmd)
        if success:
            logger.info(f"Successfully connected to SSID: {ssid}")
        else:
            logger.error(f"Failed to connect to SSID: {ssid}. Output: {output}")
        return success, output

    def ensure_hotspot(self, force: bool = False) -> Tuple[bool, str]:
        """
        Fallback mechanism to launch local Access Point.
        If connected to client Wi-Fi and not forced, does nothing.
        If offline or force=True, activates RobotHotspot so user can connect.
        Returns (success, message).
        """
        status = self.get_status()
        if status["connected"] and status["mode"] == "hotspot":
            return True, "RobotHotspot is already active."
        if status["connected"] and not force:
            return True, "Already connected to Wi-Fi."

        logger.warning("WifiManager: Activating Hotspot...")
        iface = self._get_wifi_interface()


        # Check if connection profile exists
        exists, _ = self._run_command(["con", "show", "RobotHotspot"])

        if not exists:
            logger.info(
                f"WifiManager: Creating RobotHotspot profile on interface {iface}..."
            )
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

        # Disconnect current active device if forcing hotspot while connected
        if status["connected"]:
            self._run_command(["device", "disconnect", iface])

        success, output = self._run_command(["con", "up", "RobotHotspot"])
        if success:
            logger.warning("WifiManager: Hotspot activated.")
            return True, "RobotHotspot activated successfully."
        else:
            logger.error(f"WifiManager: Failed to activate hotspot: {output}")
            return False, output or "Failed to activate RobotHotspot connection."


