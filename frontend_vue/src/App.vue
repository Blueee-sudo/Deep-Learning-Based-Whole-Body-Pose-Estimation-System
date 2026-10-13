<template>
  <el-container class="layout" :class="{ 'layout--auth': isAuthRoute }">
    <template v-if="showMainLayout">
      <el-aside width="252px" class="sidebar">
        <div class="brand-panel">
          <div class="brand-mark">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div>
            <div class="brand-title">全身姿态关键点定位系统</div>
            <div class="brand-subtitle">Human Whole-Body Pose Estimation</div>
          </div>
        </div>

        <el-menu :default-active="$route.path" router class="nav-menu">
          <el-menu-item index="/home">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/image">
            <el-icon><Picture /></el-icon>
            <span>图片检测</span>
          </el-menu-item>
          <el-menu-item index="/video">
            <el-icon><VideoCamera /></el-icon>
            <span>视频检测</span>
          </el-menu-item>
          <el-menu-item index="/realtime">
            <el-icon><Camera /></el-icon>
            <span>实时检测</span>
          </el-menu-item>
          <el-menu-item index="/history">
            <el-icon><Clock /></el-icon>
            <span>历史记录</span>
          </el-menu-item>
          <el-menu-item index="/pose-history">
            <el-icon><DataLine /></el-icon>
            <span>动作历史</span>
          </el-menu-item>
          <el-menu-item index="/pose-trends">
            <el-icon><TrendCharts /></el-icon>
            <span>趋势分析</span>
          </el-menu-item>
          <el-menu-item v-if="auth.state.user?.role_id === 1" index="/admin">
            <el-icon><UserFilled /></el-icon>
            <span>管理员</span>
          </el-menu-item>
        </el-menu>

        <div class="status-card">
          <div class="status-title">
            <el-icon><Monitor /></el-icon>
            <span>系统状态</span>
          </div>
          <div class="status-row">
            <span class="status-dot"></span>
            <span>服务正常</span>
          </div>
          <div class="status-row">
            <span class="status-dot status-dot--model"></span>
            <span>模型在线</span>
          </div>
          <div class="version">Version 1.0.0</div>
        </div>
      </el-aside>

      <el-container class="workspace">
        <el-header v-if="showHeader" class="topbar">
          <div class="topbar-left">
            <div class="menu-button">
              <el-icon><Menu /></el-icon>
            </div>
            <div>
              <div class="topbar-title">全身姿态关键点定位系统</div>
              <div class="topbar-subtitle">AI-powered pose detection and motion analysis platform</div>
            </div>
          </div>
          <div class="user-bar">
            <div v-if="auth.state.user" class="user-card">
              <el-tag size="small" effect="light" type="primary">
                {{ auth.state.user.role_id === 1 ? "管理员" : "用户" }}
              </el-tag>
              <el-avatar :size="32" class="user-avatar">
                <el-icon><UserFilled /></el-icon>
              </el-avatar>
              <span class="username">{{ auth.state.user.username }}</span>
            </div>
            <el-button v-if="!auth.state.token" size="small" type="primary" @click="go('/auth')">登录 / 注册</el-button>
            <el-button v-if="auth.state.token" size="small" class="logout-btn" @click="logout">
              <el-icon><SwitchButton /></el-icon>
              退出
            </el-button>
          </div>
        </el-header>

        <el-main class="main-area">
          <div class="page-shell">
            <router-view />
          </div>
        </el-main>
      </el-container>
    </template>

    <template v-else>
      <el-header v-if="showHeader" class="topbar topbar--public">
        <div class="topbar-left">
          <div class="menu-button">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div>
            <div class="topbar-title">全身姿态关键点定位系统</div>
            <div class="topbar-subtitle">Human Whole-Body Pose Estimation System</div>
          </div>
        </div>
        <div class="user-bar">
          <span v-if="auth.state.user" class="username">
            {{ auth.state.user.username }}（{{ auth.state.user.role_id === 1 ? "管理员" : "用户" }}）
          </span>
          <el-button v-if="!auth.state.token" size="small" type="primary" @click="go('/auth')">登录 / 注册</el-button>
          <el-button v-if="auth.state.token" size="small" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="auth-main">
        <router-view />
      </el-main>
    </template>
  </el-container>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Camera,
  Clock,
  DataAnalysis,
  DataLine,
  HomeFilled,
  Menu,
  Monitor,
  Picture,
  SwitchButton,
  TrendCharts,
  UserFilled,
  VideoCamera,
} from "@element-plus/icons-vue";
import { useAuthStore } from "./stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const showMainLayout = computed(() => auth.state.token && !route.meta?.authPage);
const showHeader = computed(() => !route.meta?.authPage);
const isAuthRoute = computed(() => Boolean(route.meta?.authPage));

function go(path) {
  router.push(path);
}
function logout() {
  auth.clearAuth();
  router.push("/auth");
}

function handleUnauthorized() {
  auth.clearAuth();
  if (route.path !== "/auth") {
    router.push("/auth");
  }
}

onMounted(async () => {
  window.addEventListener("auth:unauthorized", handleUnauthorized);
  if (auth.state.token && !route.meta?.authPage) {
    const user = await auth.refreshMe();
    if (!user) {
      router.replace("/auth");
    }
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("auth:unauthorized", handleUnauthorized);
});
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 10%, rgba(74, 144, 226, 0.14), transparent 28%),
    linear-gradient(135deg, #f5f8ff 0%, #eef4ff 46%, #f8fbff 100%);
  color: #102033;
}
.layout.layout--auth {
  height: 100%;
  min-height: 100%;
  max-height: 100%;
  overflow: hidden;
}

.sidebar {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 18px 14px;
  background:
    linear-gradient(180deg, rgba(8, 23, 54, 0.98) 0%, rgba(10, 38, 83, 0.98) 52%, rgba(15, 65, 128, 0.96) 100%),
    radial-gradient(circle at 30% 0%, rgba(86, 145, 255, 0.28), transparent 34%);
  border-right: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 18px 0 40px rgba(20, 63, 132, 0.14);
  overflow: hidden;
}
.sidebar::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    radial-gradient(circle at 24px 54px, rgba(255, 255, 255, 0.24) 0 1px, transparent 1px),
    radial-gradient(circle at 190px 124px, rgba(112, 178, 255, 0.3) 0 1px, transparent 1px);
  background-size: 160px 160px;
  opacity: 0.55;
}
.brand-panel,
.nav-menu,
.status-card {
  position: relative;
  z-index: 1;
}
.brand-panel {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 64px;
  padding: 10px 10px 18px;
  margin-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  color: #fff;
  border-radius: 14px;
  background: linear-gradient(135deg, #2f8cff 0%, #7c4dff 100%);
  box-shadow: 0 14px 28px rgba(56, 132, 255, 0.36);
}
.brand-title {
  max-width: 168px;
  color: #f8fbff;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.3;
}
.brand-subtitle {
  margin-top: 3px;
  color: rgba(222, 236, 255, 0.68);
  font-size: 11px;
  line-height: 1.25;
}
.nav-menu {
  flex: 1;
  border-right: 0;
  background: transparent;
}
.nav-menu :deep(.el-menu-item) {
  height: 46px;
  margin: 7px 0;
  padding: 0 14px !important;
  color: rgba(232, 241, 255, 0.82);
  border-radius: 14px;
  font-size: 14px;
  transition: all 0.2s ease;
}
.nav-menu :deep(.el-menu-item .el-icon) {
  color: rgba(232, 241, 255, 0.86);
  font-size: 18px;
}
.nav-menu :deep(.el-menu-item:hover) {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}
.nav-menu :deep(.el-menu-item.is-active) {
  color: #fff;
  background: linear-gradient(135deg, #2f8cff 0%, #7d4dff 100%);
  box-shadow: 0 14px 26px rgba(53, 129, 255, 0.34);
}
.nav-menu :deep(.el-menu-item.is-active .el-icon) {
  color: #fff;
}
.status-card {
  padding: 14px;
  color: rgba(235, 244, 255, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.07);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
.status-title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 10px;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 700;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}
.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
  font-size: 12px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #28e3a6;
  box-shadow: 0 0 0 4px rgba(40, 227, 166, 0.12);
}
.status-dot--model {
  background: #6aa7ff;
  box-shadow: 0 0 0 4px rgba(106, 167, 255, 0.14);
}
.version {
  margin-top: 14px;
  color: rgba(235, 244, 255, 0.58);
  font-size: 11px;
}

.workspace {
  min-width: 0;
  min-height: 100vh;
}
.topbar {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  background: rgba(255, 255, 255, 0.82);
  border-bottom: 1px solid rgba(216, 226, 244, 0.86);
  box-shadow: 0 10px 30px rgba(52, 88, 140, 0.06);
  backdrop-filter: blur(14px);
}
.topbar--public {
  width: 100%;
}
.topbar-left {
  display: flex;
  align-items: center;
  gap: 13px;
  min-width: 0;
}
.menu-button {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  color: #2262d8;
  border: 1px solid #dbe7ff;
  border-radius: 13px;
  background: linear-gradient(180deg, #ffffff 0%, #f2f7ff 100%);
}
.topbar-title {
  color: #132238;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.2px;
  line-height: 1.2;
}
.topbar-subtitle {
  margin-top: 3px;
  color: #6f8099;
  font-size: 12px;
}
.user-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  white-space: nowrap;
}
.user-card {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 6px 10px;
  border: 1px solid #e2eafd;
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(61, 96, 154, 0.08);
}
.user-avatar {
  color: #2f6ce5;
  background: linear-gradient(135deg, #ecf4ff 0%, #dfeaff 100%);
}
.username {
  color: #26384f;
  font-size: 13px;
  font-weight: 600;
}
.logout-btn {
  border-color: #dfe8f8;
  color: #37506f;
  background: #fff;
}
.main-area {
  padding: 20px 24px 28px;
  overflow: auto;
}
.page-shell {
  min-height: calc(100vh - 120px);
  padding: 18px;
  border: 1px solid rgba(220, 230, 247, 0.82);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.86) 0%, rgba(250, 253, 255, 0.92) 100%),
    radial-gradient(circle at 85% 0%, rgba(95, 148, 255, 0.12), transparent 32%);
  box-shadow: 0 18px 48px rgba(63, 94, 145, 0.1);
}
.auth-main {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 0;
  height: 100%;
  padding: 0;
  overflow: hidden;
}

@media (max-width: 1366px) {
  .sidebar {
    padding: 16px 12px;
  }
  .topbar {
    padding: 0 22px;
  }
  .main-area {
    padding: 16px 18px 22px;
  }
  .page-shell {
    padding: 14px;
    border-radius: 20px;
  }
}

@media (max-width: 1024px) {
  .sidebar {
    width: 224px !important;
  }
  .brand-title {
    font-size: 13px;
  }
  .topbar-subtitle {
    display: none;
  }
}
</style>
