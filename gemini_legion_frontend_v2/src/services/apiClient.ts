// Purpose: Centralized API client configuration (e.g., Axios instance).
// Data_Contract (Interface):
//   Default export: AxiosInstance or similar API client object.
//   Methods: get, post, put, delete, etc.
// State_Management: May handle global API state like base URL, default headers, interceptors for auth/error handling.
// Dependencies & Dependents: Uses 'axios'. Imported by all other apiService files.
// V2_Compliance_Check: Confirmed.

import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';

// Define a more structured error type
export interface ApiError {
  status?: number;
  message: string;
  detail?: string; // From FastAPI HTTPExceptions
  data?: any; // Original error data
}

const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v2',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // Increased timeout slightly
});

apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error: AxiosError) => {
    console.error('API Request Error Interceptor:', error);
    const customError: ApiError = {
      message: error.message || 'A request error occurred',
      status: error.response?.status,
      data: error.config, // Or error itself
    };
    return Promise.reject(customError);
  }
);

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    let apiError: ApiError;

    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      const serverError = error.response.data as any; // Type assertion
      apiError = {
        message: serverError?.detail || error.message || 'An error occurred',
        status: error.response.status,
        detail: serverError?.detail, // FastAPI often puts detailed messages here
        data: serverError,
      };
      console.error('API Response Error:', `Status: ${apiError.status}, Detail: ${apiError.detail || apiError.message}`, serverError);
    } else if (error.request) {
      // The request was made but no response was received
      apiError = {
        message: 'No response received from server. Check network connection or server status.',
        data: error.request,
      };
      console.error('API No Response Error:', apiError.message);
    } else {
      // Something happened in setting up the request that triggered an Error
      apiError = {
        message: error.message || 'Error setting up API request',
      };
      console.error('API Request Setup Error:', apiError.message);
    }

    // Instead of just rejecting with error, reject with the structured ApiError
    return Promise.reject(apiError);
  }
);

export default apiClient;
