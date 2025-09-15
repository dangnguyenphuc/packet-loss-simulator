import axios from 'axios';

// Create an Axios instance with default configuration
const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export async function axiosGet(url, params = {}) {
    const response = await apiClient.get(url, {
        params: params
    });
    return response.data;
}

export async function axiosPost(url, payload = {}, timeout = 60000) {
    const response = await apiClient.post(url, payload, {
        timeout
    });
    return response.data;
}

export async function axiosDelete(url, payload = {}) {
    const response = await apiClient.delete(url, { data: payload });
    return response;
}