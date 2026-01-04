
To set up the development environment:
```bash
#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# 1. Install libffi-dev only if not found in dpkg database
if ! dpkg -s libffi-dev >/dev/null 2>&1; then
    echo "Installing libffi-dev..."
    sudo apt-get install -y libffi-dev
else
    echo "libffi-dev is already installed."
fi

# 2. Install uv only if the 'uv' command is not found
# We also check the default install location just in case it's installed but not in PATH
if ! command -v uv >/dev/null 2>&1 && [ ! -f "$HOME/.cargo/bin/uv" ]; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Ensure uv is in the PATH (needed if it was just installed or if shell doesn't have it loaded)
if [ -f "$HOME/.cargo/env" ]; then
    source "$HOME/.cargo/env"
fi

uv self update

# 3. Generate certificates only if they don't exist
if [[ ! -f "cert.pem" || ! -f "key.pem" ]]; then
    echo "Generating certificates..."
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
else
    echo "Certificates already exist."
fi

# 4. Install playwright python package only if not found by uv
if ! uv pip show playwright >/dev/null 2>&1; then
    echo "Installing Playwright package..."
    uv pip install playwright
fi

# 5. Install Chromium browsers only if the directory is empty/missing
# Playwright installs to ~/.cache/ms-playwright by default. 
# We look for a chromium folder specifically.
if ! find ~/.cache/ms-playwright -type d -name "chromium-*" -quit 2>/dev/null; then
    echo "Installing Chromium..."
    uv run playwright install chromium
else
    echo "Chromium is already installed."
fi

# 6. Run the verification script
echo "Running verification..."
uv run python3 verification/verify_controller.py
```
