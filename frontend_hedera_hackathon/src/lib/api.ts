'use client';

const API_URL = process.env.NEXT_PUBLIC_API_URL;
const HEDERA_MIRROR_NODE_API = 'https://testnet.mirrornode.hedera.com/api/v1';

type Options = {
    headers?: Record<string, string>;
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
    body?: any;
};

async function request<T>(baseUrl: string, endpoint: string, options: Options = {}): Promise<T> {
    const { headers = {}, method = 'GET', body } = options;

    const config: RequestInit = {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...headers,
        },
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    const response = await fetch(`${baseUrl}${endpoint}`, config);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: response.statusText }));
        throw new Error(errorData.message || 'An API error occurred');
    }

    const responseText = await response.text();
    if (!responseText) {
        return null as T;
    }

    return JSON.parse(responseText);
}

export const api = {
    get: <T>(endpoint: string, headers?: Record<string, string>) =>
        request<T>(API_URL!, endpoint, { headers }),
    post: <T>(endpoint: string, body: any, headers?: Record<string, string>) =>
        request<T>(API_URL!, endpoint, { method: 'POST', body, headers }),
    put: <T>(endpoint: string, body: any, headers?: Record<string, string>) =>
        request<T>(API_URL!, endpoint, { method: 'PUT', body, headers }),
    delete: <T>(endpoint: string, headers?: Record<string, string>) =>
        request<T>(API_URL!, endpoint, { method: 'DELETE', headers }),
    hedera: {
        get: <T>(endpoint: string, headers?: Record<string, string>) =>
            request<T>(HEDERA_MIRROR_NODE_API, endpoint, { headers }),
    }
};