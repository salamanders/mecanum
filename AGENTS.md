
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

# 3. Install Python dependencies
echo "Installing project dependencies..."
uv sync
```
