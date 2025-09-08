import { axiosGet, axiosPost, axiosDelete } from './common.js';
import { DEVICE_ENDPOINT, PROXY_ENDPOINT } from '../constants/api.js';

export async function fetchDevices() {
    try {
        return await axiosGet(DEVICE_ENDPOINT);
    } catch (err) {
        throw new Error(`[GET] Failed to fetch devices: ${err.message}`);
    }
}

export async function fetchDeviceIp(device) {
    try {
        return await axiosGet(`${DEVICE_ENDPOINT}/${device}/ip`);
    } catch (err) {
        throw new Error(`[GET] Failed to fetch device IPs: ${err.message}`);
    }
}

export async function fetchJson(filename) {
    try {
        return await axiosGet(`/api/json/${filename}`);
    } catch (err) {
        throw new Error(`[GET] Failed to fetch ${filename}: ${err.message}`);
    }
}

export async function fetchInfo() {
    try {
        return await axiosGet(`/api/info`);
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

export function convertTimerToMs(h, m, s) {
    return (h * 3600 + m * 60 + s) * 1000;
}