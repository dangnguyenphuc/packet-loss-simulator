import axios from 'axios';

// Create an Axios instance with default configuration
const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
    // Optional: Configure CSRF if required by the backend
    // xsrfCookieName: 'csrftoken',
    // xsrfHeaderName: 'X-CSRFToken',
});

// Optional: Add response interceptor for consistent error handling
apiClient.interceptors.response.use(
    response => response,
    error => {
        // Handle errors globally (e.g., log or show user-friendly message)
        console.error('API error:', error.message);
        return Promise.reject(error);
    }
);

export async function axiosGet(url, params = {}) {
    const response = await apiClient.get(url, {
        params: params
    });
    return response.data;
}

export async function axiosPost(url, payload = {}) {
    const response = await apiClient.post(url, payload);
    return response.data;
}

export async function axiosDelete(url, payload = {}) {
    const response = await apiClient.delete(url, { data: payload });
    return response;
}