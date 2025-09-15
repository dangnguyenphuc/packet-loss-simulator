import { axiosGet, axiosPost, axiosDelete } from './common.js';
import { 
    DEVICE_ENDPOINT, 
    PROXY_ENDPOINT, 
    IP_ENDPOINT,
    JSON_ENDPOINT,
    ANDROID_ENDPOINT
} from '../constants/api.js';

export async function fetchDevices() {
    try {
        return await axiosGet(DEVICE_ENDPOINT);
    } catch (err) {
        throw new Error(`[GET] Failed to fetch devices: ${err.message}`);
    }
}

export async function fetchDeviceIp(device) {
    try {
        return await axiosGet(`${IP_ENDPOINT}/${device}`);
    } catch (err) {
        throw new Error(`[GET] Failed to fetch device IPs: ${err.message}`);
    }
}

export async function fetchJsons() {
    try {
        return await axiosGet(`${JSON_ENDPOINT}`);
    } catch (err) {
        throw new Error(`[GET] Failed to fetch JSON files: ${err.message}`);
    }
}

export async function fetchJsonContent(filename) {
    try {
        return await axiosGet(`${JSON_ENDPOINT}/${filename}`);
    } catch (err) {
        throw new Error(`[GET] Failed to fetch ${filename}: ${err.message}`);
    }
}

export async function fetchInfo(deviceId) {
    try {
        return await axiosGet(`/api/info`, {
            deviceId: deviceId
        });
    } catch (err) {
        throw new Error(`[GET] Failed to fetch audio: ${err.message}`);
    }
}

export async function deleteShape(payload, endpoint = PROXY_ENDPOINT) {
    try {
        return await axiosDelete(endpoint, payload);
    } catch (err) {
        throw new Error(`[DELETE] ${endpoint} failed: ${err.message}`);
    }
}

export async function postShape(payload = {}, endpoint = PROXY_ENDPOINT) {
    try {
        return await axiosPost(endpoint, payload);
    } catch (err) {
        throw new Error(`[POST] ${endpoint} failed: ${err.message}`);
    }
}

export async function getShape(endpoint = PROXY_ENDPOINT, ip = "") {
    try {
        const url = ip ? `${endpoint}?ip=${ip}` : endpoint;
        return await axiosGet(url);
    } catch (err) {
        throw new Error(`[GET] ${endpoint} failed: ${err.message}`);
    }
}

export async function applyConfig(payload = {}, endpoint = PROXY_ENDPOINT) {
    try {
        await deleteShape(payload, endpoint);
    } finally {
        try {
            return await postShape(payload, endpoint);
        } catch (err) {
            throw new Error("[POST] Cannot post shape");
        }
    }
}

export async function runApp(payload = {}, timeout=60000, endpoint = ANDROID_ENDPOINT) {
    try {
        return await axiosPost(endpoint, payload, timeout);
    } catch (err) {
        throw new Error(`[POST] ${endpoint} failed: ${err.message}`);
    }
}