#!/bin/bash

interfaceExists() {
    ip link show "$1" >/dev/null 2>&1
    return $?
}

while true; do
    if interfaceExists "$LAN_INTERFACE" && interfaceExists "$WAN_INTERFACE"; then
        echo "Both interfaces $LAN_INTERFACE and $WAN_INTERFACE are available."
        break
    else
        echo "Waiting for $LAN_INTERFACE and $WAN_INTERFACE to become available..."
        sleep "$RESTART_SLEEP_TIME"
    fi
done

# Remove existing qdisc rules
tc qdisc del dev "$LAN_INTERFACE" root 2>/dev/null
tc qdisc del dev "$WAN_INTERFACE" root 2>/dev/null
rm -f /var/run/AtcdVService.pid

if [ -z "$ATCD_BINARY" ]; then
    echo "Error: atcd not found in PATH"
    exit 1
fi

# Start ATCD in unsecure mode
"$ATCD_BINARY" --atcd-lan "$LAN_INTERFACE" --atcd-wan "$WAN_INTERFACE" --atcd-mode unsecure