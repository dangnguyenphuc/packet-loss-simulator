#!/bin/bash

##########################################################
# Single-port mode: Django serves Vue as static files.
# Run `make build-frontend` before this to generate static assets.
##########################################################

PROJECT_DIR="${PROJECT_DIR:-/home/dangnp/workspace/tools/loss-simulator}"
PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3.12}"
PIP_BIN="${PIP_BIN:-/usr/bin/pip3.12}"
DJANGO_PORT="${DJANGO_PORT:-8000}"

BACKEND_DIR="$PROJECT_DIR/lossSimulator"
VENV_DIR="$PROJECT_DIR/venv"

echo "[INFO] Starting Django (single-port mode) on port $DJANGO_PORT..."

if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Creating virtualenv..."
    $PYTHON_BIN -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install -r "$PROJECT_DIR/requirements.txt" -q
fi

python "$BACKEND_DIR/manage.py" migrate

nohup python "$BACKEND_DIR/manage.py" runserver "0.0.0.0:$DJANGO_PORT" > "$PROJECT_DIR/django.log" 2>&1 &

echo "[INFO] Django running at http://0.0.0.0:$DJANGO_PORT"
echo "[INFO] Log: $PROJECT_DIR/django.log"
