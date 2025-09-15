export const GUIDE_TEXT = `+ Fix90: Fixed 90% packet loss rate
+ Dynamic: Loss rate varies over time (each ... second)
+ IncreaseOnly: Same as Dynamic but loss rate always increase`

export const TOAST_TIMEOUT = 3000;
export const DEFAULT_ATC_TIMEOUT = 10000;

/*
\\\\\\\\\\\\\\\\\\\\\\\\
Emit events: -----------
\\\\\\\\\\\\\\\\\\\\\\\\
*/
export const EVENT_UPDATE_MODEL = "update:modelValue";

export const EVENT_OPEN_TOAST = "open:Toast";
export const EVENT_CLOSE_TOAST = "close:Toast";

export const EVENT_UPDATE_DEVICE = "update:device";
export const EVENT_UPDATE_DEVICE_IP = "update:deviceIp";
export const EVENT_FETCH_DEVICE = "fetch:device";

export const EVENT_UPDATE_TIMER_H = "update:hour";
export const EVENT_UPDATE_TIMER_M = "update:minute";
export const EVENT_UPDATE_TIMER_S = "update:second";