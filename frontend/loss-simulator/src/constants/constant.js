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
	{
		name: "2G-DevelopingRural",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"650\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":\"2\"},\"rate\":\"20\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"650\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":\"2\"},\"rate\":\"18\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "2G-DevelopingUrban",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"650\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"35\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"650\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"32\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "3G-Average",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"100\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"780\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"100\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"330\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "3G-Good",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"90\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"850\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"100\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"420\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "3G-Poor",
		data: "{\"down\":{\"corruption\":{\"correlation\":4,\"percentage\":1.2},\"delay\":{\"correlation\":6,\"delay\":\"220\",\"jitter\":80},\"iptables_options\":[],\"loss\":{\"correlation\":3,\"percentage\":5.0},\"rate\":\"450\",\"reorder\":{\"correlation\":3,\"gap\":6,\"percentage\":1.5}},\"up\":{\"corruption\":{\"correlation\":2,\"percentage\":0.7},\"delay\":{\"correlation\":5,\"delay\":\"240\",\"jitter\":90},\"iptables_options\":[],\"loss\":{\"correlation\":2,\"percentage\":6.0},\"rate\":\"180\",\"reorder\":{\"correlation\":2,\"gap\":6,\"percentage\":1.5}}}",
	},
	{
		name: "4G-Average",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"40\",\"jitter\":5},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0.5},\"rate\":\"15000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0.5}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"50\",\"jitter\":5},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0.5},\"rate\":\"5000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0.5}}}",
	},
	{
		name: "4G-Good",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"20\",\"jitter\":2},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"30000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"25\",\"jitter\":2},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"10000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "4G-Poor",
		data: "{\"down\":{\"corruption\":{\"correlation\":4,\"percentage\":0.8},\"delay\":{\"correlation\":5,\"delay\":\"150\",\"jitter\":40},\"iptables_options\":[],\"loss\":{\"correlation\":2,\"percentage\":3.5},\"rate\":\"7000\",\"reorder\":{\"correlation\":3,\"gap\":5,\"percentage\":1.5}},\"up\":{\"corruption\":{\"correlation\":2,\"percentage\":0.5},\"delay\":{\"correlation\":4,\"delay\":\"160\",\"jitter\":45},\"iptables_options\":[],\"loss\":{\"correlation\":1,\"percentage\":4.0},\"rate\":\"2000\",\"reorder\":{\"correlation\":2,\"gap\":5,\"percentage\":1.5}}}",
	},
	{
		name: "5G-Average",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"15\",\"jitter\":3},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0.2},\"rate\":\"150000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0.1}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"18\",\"jitter\":3},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0.1},\"rate\":\"50000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0.1}}}",
	},
	{
		name: "5G-Good",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"8\",\"jitter\":1},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"300000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"10\",\"jitter\":1},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"100000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "5G-Poor",
		data: "{\"down\":{\"corruption\":{\"correlation\":5,\"percentage\":0.8},\"delay\":{\"correlation\":5,\"delay\":\"80\",\"jitter\":30},\"iptables_options\":[],\"loss\":{\"correlation\":2,\"percentage\":3.0},\"rate\":\"50000\",\"reorder\":{\"correlation\":3,\"gap\":5,\"percentage\":2.0}},\"up\":{\"corruption\":{\"correlation\":4,\"percentage\":1.0},\"delay\":{\"correlation\":5,\"delay\":\"90\",\"jitter\":40},\"iptables_options\":[],\"loss\":{\"correlation\":2,\"percentage\":4.0},\"rate\":\"20000\",\"reorder\":{\"correlation\":3,\"gap\":5,\"percentage\":2.0}}}",
	},
	{
		name: "Cable",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"2\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"6000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"2\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"1000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "DSL",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"5\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"2000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"5\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0},\"rate\":\"256\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "Edge-Average",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"400\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":\"0\"},\"rate\":\"240\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"440\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":\"0\"},\"rate\":\"200\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "Edge-Good",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"350\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":\"0\"},\"rate\":\"250\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"370\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":\"0\"},\"rate\":\"200\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "Edge-Lossy",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"400\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":\"1\"},\"rate\":\"240\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0},\"delay\":{\"correlation\":0,\"delay\":\"440\",\"jitter\":0},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":\"1\"},\"rate\":\"200\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0}}}",
	},
	{
		name: "Wifi-Average",
		data: "{\"down\":{\"corruption\":{\"correlation\":1,\"percentage\":0.1},\"delay\":{\"correlation\":1,\"delay\":\"15\",\"jitter\":5},\"iptables_options\":[],\"loss\":{\"correlation\":2,\"percentage\":0.8},\"rate\":\"40000\",\"reorder\":{\"correlation\":1,\"gap\":0,\"percentage\":0.3}},\"up\":{\"corruption\":{\"correlation\":1,\"percentage\":0.1},\"delay\":{\"correlation\":1,\"delay\":\"20\",\"jitter\":6},\"iptables_options\":[],\"loss\":{\"correlation\":2,\"percentage\":1.0},\"rate\":\"20000\",\"reorder\":{\"correlation\":1,\"gap\":0,\"percentage\":0.3}}}",
	},
	{
		name: "Wifi-Good",
		data: "{\"down\":{\"corruption\":{\"correlation\":0,\"percentage\":0.02},\"delay\":{\"correlation\":0,\"delay\":\"5\",\"jitter\":1},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0.1},\"rate\":\"120000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0.05}},\"up\":{\"corruption\":{\"correlation\":0,\"percentage\":0.02},\"delay\":{\"correlation\":0,\"delay\":\"6\",\"jitter\":1},\"iptables_options\":[],\"loss\":{\"correlation\":0,\"percentage\":0.1},\"rate\":\"80000\",\"reorder\":{\"correlation\":0,\"gap\":0,\"percentage\":0.05}}}",
	},
	{
		name: "Wifi-Poor",
		data: "{\"down\":{\"corruption\":{\"correlation\":1,\"percentage\":0.1},\"delay\":{\"correlation\":1,\"delay\":\"15\",\"jitter\":5},\"iptables_options\":[],\"loss\":{\"correlation\":2,\"percentage\":0.8},\"rate\":\"40000\",\"reorder\":{\"correlation\":1,\"gap\":0,\"percentage\":0.3}},\"up\":{\"corruption\":{\"correlation\":1,\"percentage\":0.1},\"delay\":{\"correlation\":1,\"delay\":\"20\",\"jitter\":6},\"iptables_options\":[],\"loss\":{\"correlation\":2,\"percentage\":1.0},\"rate\":\"20000\",\"reorder\":{\"correlation\":1,\"gap\":0,\"percentage\":0.3}}}",
	},
]

export const EVAL_RTT = [ 
	200, 
	500,
	700, 
	950,
	1200, 
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
	30,
	50,
	70,
	85,
	100
]

// Paired severity sweep (index-aligned): sub-case i combines
// EVAL_SUBCASE_LOSS[i] with EVAL_SUBCASE_DELAY[i], from clean to worst-case.
export const EVAL_SUBCASE_LOSS = [
	0,
	5,
	10,
	15,
	20,
	30,
	40,
	50,
	70,
	90,
]
export const EVAL_SUBCASE_DELAY = [
	50,
	80,
	120,
	160,
	200,
	300,
	400,
	600,
	900,
	1200,
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