import axios from "axios";

const client = axios.create({
  baseURL: "/api",
  timeout: 120000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (resp) => resp,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      const url = String(err?.config?.url || "");
      const isLoginOrRegister = url.includes("/auth/login/") || url.includes("/auth/register/");
      if (!isLoginOrRegister && typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("auth:unauthorized"));
      }
    }
    return Promise.reject(err);
  }
);

export default client;
