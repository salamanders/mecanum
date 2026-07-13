The "modern simple way" (and the most robust) is to create a **Systemd Service**.
It creates one text file that tells the Pi: *"Wait for WiFi, then run this command, and restart it if it crashes."*

### Step 1: Get your details

You need to know exactly where your code lives.

1. SSH into your Pi.
2. Navigate to your robot folder: `cd mecanum` (or whatever you named it).
3. Run `make install` to ensure all dependencies are installed.
4. Type `pwd` and copy the output. (e.g., `/home/pi/mecanum`)
5. Type `whoami` to confirm your username. (e.g., `pi` or `admin`)
6. Type `which uv` to get the path to uv. (e.g. `/home/pi/.local/bin/uv`)

### Step 2: Create the Service File

Run this command to create the file:

```bash
sudo nano /etc/systemd/system/robot.service

```

Paste this text into the file. **Important:** Replace `/home/pi/mecanum` with the path you copied in Step 1, and `pi`
with your username if it's different.

```ini
[Unit]
Description=Robot Web Controller
After=network-online.target
Wants=network-online.target

[Service]
# Update to your username from "whoami"
User=pi
# Replace /home/pi/mecanum with the path you copied in Step 1 (where you cloned the github repo)
WorkingDirectory=/home/pi/mecanum
# We use uv to run the app. Replace /home/pi/.local/bin/uv with the result of `which uv` from Step 1.
ExecStart=/home/pi/.local/bin/uv run python3 app.py

# Auto-restart if it crashes (e.g. WiFi blip)
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

```

**Why this is better than the old way:**

* `After=network-online.target`: It politely waits until the WiFi is actually connected before launching.
* `Restart=always`: If the code crashes (or you kill it), it pops right back up after 5 seconds.

### Step 3: Enable it

Save the file (Ctrl+O, Enter) and exit (Ctrl+X). Then run these two commands:

```bash
# 1. Tell Linux to scan for the new file
sudo systemctl daemon-reload

# 2. Enable it so it runs on every boot
sudo systemctl enable robot.service

```

### Step 4: Test it immediately

You don't have to reboot to test it. Just start it now:

```bash
sudo systemctl start robot.service

```

Check if it is running:

```bash
sudo systemctl status robot.service

```

* **Green Light:** If you see "Active: active (running)", navigate to your phone browser (`https://...`) and drive!
* **Red Light:** If it failed, read the error message at the bottom of that status screen. It usually means a typo in
  the path (e.g., it can't find `app.py`).

### How to update your code later

Since the service runs in the background, you can't just edit the file and run it again manually (you'll get "Address
already in use" errors).

When you change your code (like tweaking speed), do this:

1. Edit `app.py`.
2. Run `sudo systemctl restart robot` to load the changes.