// Purpose: Centralized API client configuration (e.g., Axios instance).
// Data_Contract (Interface):
//   Default export: AxiosInstance or similar API client object.
//   Methods: get, post, put, delete, etc.
// State_Management: May handle global API state like base URL, default headers, interceptors for auth/error handling.
// Dependencies & Dependents: Uses 'axios'. Imported by all other apiService files.
// V2_Compliance_Check: Confirmed.

import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';

const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v2', // Default base URL for V2 API, proxy will handle routing
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Optional: Request Interceptor (e.g., for adding auth tokens)
apiClient.interceptors.request.use(
  (config) => {
    // const token = localStorage.getItem('authToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error: AxiosError) => {
    console.error('API Request Error Interceptor:', error);
    return Promise.reject(error);
  }
);

// Optional: Response Interceptor (e.g., for global error handling)
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    // Handle specific error codes globally if needed
    // if (error.response?.status === 401) {
    //   // e.g., redirect to login
    //   console.error('Unauthorized, redirecting to login...');
    // }
    console.error('API Response Error Interceptor:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;
