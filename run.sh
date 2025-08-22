#!/bin/bash

##########################################################

# TODO: 
### 1. Connect to Anh Tien (tiennd3) network
### 2. Change project dir variable to your project path

##########################################################

# CONFIG
PROJECT_DIR="/home/dangnp/workspace/loss-simulator"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_BIN="/usr/bin/python3.12"
PIP_BIN="/usr/bin/pip3.12"
PORT=8000
DJANGO_MAIN_APP_DIR="$PROJECT_DIR/lossSimulator"

echo "[INFO] Starting setup for Django project..."

# -------------------------------
# 1. Check and install Python 3.12
# -------------------------------
if ! command -v python3.12 &> /dev/null; then
    echo "[INFO] Python 3.12 not found. Installing..."
    sudo apt update
    sudo apt install -y python3.12 python3.12-venv python3.12-distutils nmap
fi

# -------------------------------
# 2. Check and install pip3.12
# -------------------------------
if ! command -v pip3.12 &> /dev/null; then
    echo "[INFO] pip3.12 not found. Installing..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.12
fi

# -------------------------------
# 3. Create venv if missing
# -------------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Virtualenv not found. Creating..."
    $PYTHON_BIN -m venv "$VENV_DIR"
fi

# -------------------------------
# 4. Reactivate venv
# -------------------------------
if [ -n "$VIRTUAL_ENV" ]; then
    echo "[INFO] Deactivating current venv..."
    deactivate
fi

echo "[INFO] Activating virtualenv..."
source "$VENV_DIR/bin/activate"

# -------------------------------
# 5. Install dependencies
# -------------------------------
cd "$PROJECT_DIR" || { echo "[ERROR] Cannot cd into $PROJECT_DIR"; exit 1; }

if [ -f "requirements.txt" ]; then
    echo "[INFO] Installing dependencies..."
    pip install -r requirements.txt
else
    echo "[WARN] requirements.txt not found, skipping pip install"
fi

# -------------------------------
# 6. Detect host IP in 10.42.0.0/16
# -------------------------------
HOST_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)10\.42\.\d+\.\d+' | head -n1)

if [ -z "$HOST_IP" ]; then
    echo "[ERROR] Could not find IP in 10.42.0.0/16 range!"
    exit 1
fi

echo "[INFO] Found host IP: $HOST_IP"

# -------------------------------
# 7. Run Django
# -------------------------------
cd "$DJANGO_MAIN_APP_DIR"
python manage.py migrate
echo "[INFO] Running Django server at https://$HOST_IP:$PORT/"
python manage.py runserver "$HOST_IP:$PORT"

