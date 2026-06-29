import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

// Interceptor: injeta o JWT (organizador/cerimonialista) nas requisições, quando presente.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("celebra15_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
