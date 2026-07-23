import json
import os
import sys
import unittest
from unittest.mock import patch

# Ensure we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, wifi
from wifi_manager import WifiNetwork


class TestWifiEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_wifi_page(self):
        """Test the HTML page loads."""
        response = self.app.get("/wifi")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Wi-Fi Setup", response.data)

    def test_wifi_status_endpoint(self):
        """Test status endpoint structure."""
        # Mock the underlying wifi manager call
        with patch.object(wifi, "get_status") as mock_status:
            mock_status.return_value = {
                "connected": True,
                "ssid": "TestNet",
                "ip": "1.2.3.4",
                "mode": "client",
            }

            response = self.app.get("/api/wifi/status")
            data = json.loads(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["ssid"], "TestNet")
            self.assertTrue(data["connected"])

    def test_wifi_scan_endpoint(self):
        """Test scan endpoint returns list."""
        with patch.object(wifi, "scan_networks") as mock_scan:
            mock_scan.return_value = [
                WifiNetwork("NetA", 90, "WPA2"),
                WifiNetwork("NetB", 50, "Open"),
            ]

            response = self.app.get("/api/wifi/scan")
            data = json.loads(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["ssid"], "NetA")

    def test_wifi_connect_endpoint_success(self):
        """Test connection success."""
        with patch.object(wifi, "connect_to") as mock_connect:
            mock_connect.return_value = (True, "Connected!")

            payload = {"ssid": "MyNet", "password": "pass"}
            response = self.app.post(
                "/api/wifi/connect",
                data=json.dumps(payload),
                content_type="application/json",
            )
            data = json.loads(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(data["success"])
            mock_connect.assert_called_with("MyNet", "pass")

    def test_wifi_connect_endpoint_missing_ssid(self):
        """Test connection fails without SSID."""
        response = self.app.post(
            "/api/wifi/connect",
            data=json.dumps({"password": "pass"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_get_local_ip_fallback(self):
        """Test that get_local_ip falls back to wifi status IP when socket fails (offline mode)."""
        from app import get_local_ip
        import socket
        with patch.object(socket.socket, "connect", side_effect=OSError("Network unreachable")):
            with patch.object(wifi, "get_status", return_value={"ip": "10.42.0.1"}):
                self.assertEqual(get_local_ip(), "10.42.0.1")

    def test_get_wifi_interface_detection(self):
        """Test parsing of nmcli device list for wifi interface."""
        with patch.object(wifi, "is_mock", False):
            with patch.object(wifi, "_run_command", return_value=(True, "eth0:ethernet\nwlan1:wifi")):
                self.assertEqual(wifi._get_wifi_interface(), "wlan1")


if __name__ == "__main__":
    unittest.main()
