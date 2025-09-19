#!/bin/bash

##########################################################
# Setup script for Django + Vue (Vuetify) project
# 
# - Backend: Django (Python 3.12)
# - Frontend: Vue 3 + Vite (Vuetify)
##########################################################

# CONFIG
## Passed from makefile or default
PROJECT_DIR="${PROJECT_DIR:-/home/dangnp/workspace/tools/loss-simulator}"
PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3.12}"
PIP_BIN="${PIP_BIN:-/usr/bin/pip3.12}"
DJANGO_PORT="${DJANGO_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

## hardcode
BACKEND_DIR="$PROJECT_DIR/lossSimulator"
FRONTEND_DIR="$PROJECT_DIR/frontend/loss-simulator"
VENV_DIR="$PROJECT_DIR/venv"


echo "[INFO] Starting setup for Django + Vue project..."

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
# 3. Check and install Node.js (>=21)
# -------------------------------
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v | sed 's/v//; s/\..*//')
    if [ "$NODE_VERSION" -lt 21 ]; then
        echo "[INFO] Node.js version < 21 detected (v$NODE_VERSION). Upgrading..."
        curl -fsSL https://deb.nodesource.com/setup_21.x | sudo -E bash -
        sudo apt install -y nodejs
    else
        echo "[INFO] Node.js v$(node -v) is already installed."
    fi
else
    echo "[INFO] Node.js not found. Installing v21..."
    curl -fsSL https://deb.nodesource.com/setup_21.x | sudo -E bash -
    sudo apt install -y nodejs
fi

# -------------------------------
# 4. Create venv if missing
# -------------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Virtualenv not found. Creating..."
    $PYTHON_BIN -m venv "$VENV_DIR"
fi

# -------------------------------
# 5. Reactivate venv
# -------------------------------
if [ -n "$VIRTUAL_ENV" ]; then
    echo "[INFO] Deactivating current venv..."
    deactivate
fi

echo "[INFO] Activating virtualenv..."
source "$VENV_DIR/bin/activate"

# -------------------------------
# 6. Install backend dependencies
# -------------------------------

if [ -f "requirements.txt" ]; then
    echo "[INFO] Installing backend dependencies..."
    pip install -r $PROJECT_DIR/requirements.txt
else
    echo "[WARN] requirements.txt not found, skipping pip install"
fi

# -------------------------------
# 7. Run Django backend in background
# -------------------------------
python "$BACKEND_DIR/manage.py" migrate
echo "[INFO] Starting Django server at http://127.0.0.1:$DJANGO_PORT/"
nohup python "$BACKEND_DIR/manage.py" runserver "0.0.0.0:$DJANGO_PORT" > "$PROJECT_DIR/django.log" 2>&1 &

# -------------------------------
# 8. Run frontend (Vue + Vuetify) in background
# -------------------------------

if [ ! -d "node_modules" ]; then
    echo "[INFO] node_modules not found. Running npm install..."
    npm install --prefix $FRONTEND_DIR
fi

echo "[INFO] Starting frontend (Vue + Vite) at http://127.0.0.1:$FRONTEND_PORT/"
nohup npm run dev --prefix $FRONTEND_DIR -- --host 0.0.0.0 --port $FRONTEND_PORT > "$PROJECT_DIR/frontend.log" 2>&1 &

echo "[INFO] Backend and frontend are running in background."
echo "[INFO] Logs:"
echo "  - Django:   $PROJECT_DIR/django.log"
echo "  - Frontend: $PROJECT_DIR/frontend.log"
