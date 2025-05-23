import axios from "axios";
import Swal from "sweetalert2";
import { baseUrl } from "../constant/utils";

const apiUrl = baseUrl

export const axiosInstance = axios.create({
    baseURL: apiUrl,
    headers: {
        // 'Content-Type': 'application/json',
    }
});

axiosInstance.interceptors.request.use(
    (config) => {
        const token = sessionStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);
axiosInstance.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error?.response?.status === 401) {
            Swal.fire({
                toast: true,
                icon: "error",
                title: "Oops...",
                text: error?.response?.data?.detail,
                showConfirmButton: false,
                timer: 1500,
            });
            setTimeout(() => {
                sessionStorage.removeItem('token');
                window.location.href = '#/login';
            }, 1500);
        }
        return Promise.reject(error);
    }
);
