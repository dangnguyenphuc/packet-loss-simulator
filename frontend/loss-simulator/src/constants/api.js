export const JSON_ENDPOINT = '/api/json';
export const DEVICE_ENDPOINT = '/api/devices';
export const IP_ENDPOINT = (device) => `${DEVICE_ENDPOINT}/${device}/ip`;
export const PROXY_ENDPOINT = '/api/proxy/shape';
export const ANDROID_TASK_ENDPOINT = 'api/tasks';
export const ANDROID_TASK_RUN_ENDPOINT = `${ANDROID_TASK_ENDPOINT}/run`;
export const ANDROID_TASK_DETAIL_ENDPOINT = (task_id) => `${ANDROID_TASK_ENDPOINT}/${task_id}`;
export const STORE_FOLDER_ENDPOINT = (folder) => `/api/files/${folder}`;
export const STAT_ENDPOINT = '/api/stats';

export const MONITORING_INTERVAL = 10000;
export const DEFAULT_REQUEST_TIMEOUT = 5000;