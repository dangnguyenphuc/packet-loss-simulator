#!/bin/bash

# Declare network interface variables
LAN_INTERFACE="wlp4s0"
WAN_INTERFACE="eno1"

# Activate virtual environment
deactivate
source isoEnv/bin/activate

# Clean up old qdisc rules
sudo tc qdisc del dev $LAN_INTERFACE root
sudo tc qdisc del dev $WAN_INTERFACE root

# Start ATCD in unsecure mode
sudo atcd --atcd-lan $LAN_INTERFACE --atcd-wan $WAN_INTERFACE --atcd-mode unsecure --daemon

# Launch Django server in background
cd atcui
nohup python manage.py runserver 0.0.0.0:8080 > /dev/null 2>&1 &
