import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "./stores/auth";

import HomeView from "./views/HomeView.vue";
import AuthEntryView from "./views/AuthEntryView.vue";
import LoginView from "./views/LoginView.vue";
import RegisterView from "./views/RegisterView.vue";
import ImageInferView from "./views/ImageInferView.vue";
import VideoInferView from "./views/VideoInferView.vue";
import RealtimeView from "./views/RealtimeView.vue";
import HistoryView from "./views/HistoryView.vue";
import PoseHistoryView from "./views/PoseHistoryView.vue";
import PoseTrendView from "./views/PoseTrendView.vue";
import AdminView from "./views/AdminView.vue";

const routes = [
  { path: "/", redirect: "/image" },
  { path: "/auth", component: AuthEntryView, meta: { publicOnly: true, authPage: true } },
  { path: "/login", component: LoginView, meta: { publicOnly: true, legacyAuthRoute: true } },
  { path: "/register", component: RegisterView, meta: { publicOnly: true, legacyAuthRoute: true } },
  { path: "/home", component: HomeView, meta: { requiresAuth: true } },
  { path: "/image", component: ImageInferView, meta: { requiresAuth: true } },
  { path: "/video", component: VideoInferView, meta: { requiresAuth: true } },
  { path: "/realtime", component: RealtimeView, meta: { requiresAuth: true } },
  { path: "/history", component: HistoryView, meta: { requiresAuth: true } },
  { path: "/pose-history", component: PoseHistoryView, meta: { requiresAuth: true } },
  { path: "/pose-trends", component: PoseTrendView, meta: { requiresAuth: true } },
  { path: "/admin", component: AdminView, meta: { requiresAuth: true, requiresAdmin: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  const token = auth.state.token;
  const user = auth.state.user;

  if (to.meta.legacyAuthRoute) return "/auth";
  if (to.meta.requiresAuth && !token) return "/auth";
  if (to.meta.publicOnly && token) return "/image";
  if (to.meta.requiresAdmin) {
    const u = user || (await auth.refreshMe());
    if (!u || u.role_id !== 1) return "/image";
  }
  return true;
});

const AUTH_SCROLL_LOCK = "auth-page-lock-scroll";

router.afterEach((to) => {
  const root = document.documentElement;
  if (to.meta?.authPage) {
    root.classList.add(AUTH_SCROLL_LOCK);
    document.body.classList.add(AUTH_SCROLL_LOCK);
  } else {
    root.classList.remove(AUTH_SCROLL_LOCK);
    document.body.classList.remove(AUTH_SCROLL_LOCK);
  }
});

export default router;
