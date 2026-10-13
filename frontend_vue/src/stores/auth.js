import { reactive } from "vue";
import { meApi } from "../api/auth";

const state = reactive({
  token: localStorage.getItem("token") || "",
  user: (() => {
    try {
      return JSON.parse(localStorage.getItem("user") || "null");
    } catch {
      return null;
    }
  })(),
});

export function useAuthStore() {
  const setAuth = (token, user) => {
    state.token = token;
    state.user = user;
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
  };

  const clearAuth = () => {
    state.token = "";
    state.user = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  const refreshMe = async () => {
    if (!state.token) return null;
    try {
      const user = await meApi();
      state.user = user;
      localStorage.setItem("user", JSON.stringify(user));
      return user;
    } catch {
      clearAuth();
      return null;
    }
  };

  return { state, setAuth, clearAuth, refreshMe };
}
