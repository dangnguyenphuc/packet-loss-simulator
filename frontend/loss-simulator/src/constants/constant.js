export const GUIDE_TEXT = `Requirements: 
	- Android device already connected to current PC
	- Android device already allowed neccessary permissions to run the ZrtcDemoApp
	- Android device already connected to ATC network

1. Device Selector panel is used to choose device and the right network interface using ATC network.
2. After choosing device, there's information panel to display all information about storing audio path, storing log path, ...
3. Final panel is used to set ATC config(s) and start running ZrtcDemoApp on Android device:
	+ Can have multiple run
	+ Each run can used multiple ATC config(s)`;

export const TOAST_TIMEOUT = 3000;
export const DEFAULT_ATC_TIMEOUT = 10000;
export const MAX_RETRIES = 5;
export const RETRY_DELAY = 2000;
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

export const EVENT_START_APP = "start:AndroidApp";
export const EVENT_STOP_APP = "stop:AndroidApp";