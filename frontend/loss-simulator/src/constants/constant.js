export const GUIDE_TEXT = `Requirements:
	- Android device already had Zrtc Demo App (if not install by the button below)
	- Android device already connected to current PC
	- Android device already allowed neccessary permissions to run the ZrtcDemoApp
	- Android device already connected to ATC network`;

export const TOAST_TIMEOUT = 3000;
export const DEFAULT_ATC_TIMEOUT = 20000;
export const MAX_RETRIES = 3;
export const RETRY_DELAY = 2500;

export const BENCHMARK_DURATION = 2*60*1000;

export const MAX_CONFIG_SIZE = 50;

export const EVAL_COMPLEX = [

	6,
	7,
	8,
	9,
	10
];

export const EVAL_DEC_COMPLEX = [
	5,
	6,
	7,
	8,
	9,
	10
];

export const EVAL_NETWORK_TYPE = [
	// 3g-good
	{
		name: "3g-good",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"90\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"850\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"100\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"420\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}", 
	},
	// 4g-good	
	{
		name: "4g-good",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"20\",\"jitter\":2},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"30000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"25\",\"jitter\":2},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"10000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	}

]
export const EVAL_LOSS_PERCENTAGE = [
	0, 
	10, 
	20, 
	30, 
	35, 
	40, 
	45, 
	50, 
	60, 
	70, 
	75, 
	80, 
	90
]
export const EVAL_NORMAL_AND_PLC = [
	'normal', 
	'plc',
]
export const EVAL_DRED = [
	0, 
	20, 
	40, 
	60, 
	80, 
	90
]

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

export const EVENT_START_MONITORING = "start:Monitoring";
export const EVENT_STOP_MONITORING = "stop:Monitoring";
export const EVENT_RESET_MONITORING = "reset:Monitoring";