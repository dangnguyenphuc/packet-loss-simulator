export const GUIDE_TEXT = `+ Fix90: Fixed 90% packet loss rate
+ Dynamic: Loss rate varies over time (each ... second)
+ IncreaseOnly: Same as Dynamic but loss rate always increase`

export const TOAST_TIMEOUT = 3000;


/*
\\\\\\\\\\\\\\\\\\\\\\\\
Emit events: -----------
\\\\\\\\\\\\\\\\\\\\\\\\
*/

export const EVENT_OPEN_TOAST = "open:Toast";
export const EVENT_CLOSE_TOAST = "close:Toast";

export const EVENT_UPDATE_DEVICE = "update:device"
export const EVENT_UPDATE_DEVICE_IP = "update:deviceIp"