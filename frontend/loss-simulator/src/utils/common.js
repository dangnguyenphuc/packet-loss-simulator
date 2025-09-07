import axios from 'axios';

export async function axiosGet(url) {
    const response = await axios.get(url);
    return response.data;
}

export async function axiosPost(url, payload = {}, headers = { 'Content-Type': 'application/json' }) {
    const response = await axios.post(url, payload, { headers });
    return response.data;
}

export async function axiosDelete(url, payload = {}, headers = { 'Content-Type': 'application/json' }) {
    const response = await axios.delete(url, { headers, data: payload });
    return response;
}