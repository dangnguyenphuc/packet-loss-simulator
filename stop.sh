#!/bin/bash

##########################################################
# Stop script for Django + Vue (Vuetify) project
##########################################################

DJANGO_PORT="${DJANGO_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

echo "[INFO] Stopping Django + Vue project..."

# Function to kill process on port
killPort() {
    PORT=$1
    PID=$(lsof -ti:$PORT)
    if [ -n "$PID" ]; then
        echo "[INFO] Killing process on port $PORT (PID: $PID)"
        kill -9 $PID
    else
        echo "[INFO] No process found on port $PORT"
    fi
}

# Stop Django (backend)
killPort $DJANGO_PORT

# Stop Vue (frontend)
killPort $FRONTEND_PORT

echo "[INFO] All done."
