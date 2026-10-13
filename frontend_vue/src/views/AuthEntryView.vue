<template>
  <div class="auth-page">
    <div class="bg-mesh"></div>
    <div class="bg-grid"></div>
    <div class="bg-glow glow-left"></div>
    <div class="bg-glow glow-right"></div>

    <section class="auth-shell">
      <aside class="intro-panel">
        <div class="brand-pill">
          <el-icon><Aim /></el-icon>
          <span>AI Pose Estimation Platform</span>
        </div>
        <h1 class="intro-title">全身姿态关键点定位系统</h1>
        <p class="intro-subtitle">
          基于 Django、Vue 与深度学习姿态估计模型，提供图片、视频、实时摄像头三类检测入口，
          支持全身 133 个关键点定位、多动作姿态评分和历史趋势分析。
        </p>

        <div class="capability-grid">
          <div class="capability-card">
            <span>133</span>
            <p>全身关键点</p>
          </div>
          <div class="capability-card">
            <span>3</span>
            <p>检测模式</p>
          </div>
          <div class="capability-card">
            <span>5</span>
            <p>动作分析</p>
          </div>
        </div>

        <div class="feature-list">
          <div class="feature-item">
            <div class="feature-icon"><el-icon><Picture /></el-icon></div>
            <div>
              <h3>图片 / 视频 / 实时检测</h3>
              <p>覆盖单图推理、视频处理与摄像头实时分析，适配常见姿态检测场景。</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon"><el-icon><DataLine /></el-icon></div>
            <div>
              <h3>动作评分与趋势追踪</h3>
              <p>支持深蹲、平板支撑、俯卧撑、臀桥、仰卧起坐的动作质量分析。</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon"><el-icon><Files /></el-icon></div>
            <div>
              <h3>记录管理与结果导出</h3>
              <p>检测记录、动作历史、模型指标集中管理，便于回溯、展示和答辩。</p>
            </div>
          </div>
        </div>

        <div class="flow-card">
          <span>数据输入</span>
          <i></i>
          <span>关键点定位</span>
          <i></i>
          <span>动作分析</span>
          <i></i>
          <span>结果沉淀</span>
        </div>
      </aside>

      <section class="auth-panel">
        <el-card class="auth-card" shadow="never">
          <div class="auth-badge">
            <el-icon><Connection /></el-icon>
            <span>Secure Access</span>
          </div>
          <div class="card-header">
            <h2>欢迎进入系统</h2>
            <p>登录后可访问图片检测、视频姿态检测、实时检测、历史记录与趋势分析功能。</p>
          </div>

          <el-tabs v-model="activeTab" stretch class="auth-tabs">
            <el-tab-pane label="登录" name="login">
              <el-form :model="loginForm" label-position="top" class="auth-form">
                <el-form-item label="用户名">
                  <el-input
                    v-model="loginForm.username"
                    placeholder="请输入用户名"
                    size="large"
                    clearable
                    @keyup.enter="onLogin"
                  >
                    <template #prefix>
                      <el-icon><User /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item label="密码">
                  <el-input
                    v-model="loginForm.password"
                    type="password"
                    placeholder="请输入密码"
                    size="large"
                    show-password
                    @keyup.enter="onLogin"
                  >
                    <template #prefix>
                      <el-icon><Lock /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <el-button class="submit-btn" type="primary" size="large" :loading="loading" @click="onLogin">
                  {{ loading ? "登录中..." : "登录并进入姿态分析平台" }}
                </el-button>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="注册" name="register">
              <el-form :model="registerForm" label-position="top" class="auth-form">
                <el-form-item label="用户名">
                  <el-input
                    v-model="registerForm.username"
                    placeholder="不少于 3 个字符"
                    size="large"
                    clearable
                    @keyup.enter="onRegister"
                  >
                    <template #prefix>
                      <el-icon><User /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item label="邮箱">
                  <el-input
                    v-model="registerForm.email"
                    placeholder="请输入常用邮箱"
                    size="large"
                    clearable
                    @keyup.enter="onRegister"
                  >
                    <template #prefix>
                      <el-icon><Message /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item label="密码">
                  <el-input
                    v-model="registerForm.password"
                    type="password"
                    placeholder="不少于 8 位"
                    size="large"
                    show-password
                    @keyup.enter="onRegister"
                  >
                    <template #prefix>
                      <el-icon><Lock /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <el-button class="submit-btn" type="primary" size="large" :loading="loading" @click="onRegister">
                  {{ loading ? "注册中..." : "创建账号并进入系统" }}
                </el-button>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <div class="auth-tips">
            <span>登录后开放</span>
            <b>图片检测</b>
            <b>视频姿态检测</b>
            <b>实时检测</b>
          </div>
        </el-card>
      </section>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  Aim,
  Connection,
  DataLine,
  Files,
  Lock,
  Message,
  Picture,
  User,
} from "@element-plus/icons-vue";
import { loginApi, registerApi } from "../api/auth";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const activeTab = ref("login");
const loginForm = reactive({ username: "", password: "" });
const registerForm = reactive({ username: "", email: "", password: "" });

async function onLogin() {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning("请填写完整登录信息");
    return;
  }
  loading.value = true;
  try {
    const data = await loginApi(loginForm);
    auth.setAuth(data.access_token, data.user);
    ElMessage.success("登录成功");
    router.push("/image");
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "登录失败");
  } finally {
    loading.value = false;
  }
}

async function onRegister() {
  if (!registerForm.username || !registerForm.email || !registerForm.password) {
    ElMessage.warning("请填写完整注册信息");
    return;
  }
  loading.value = true;
  try {
    await registerApi(registerForm);
    const data = await loginApi({
      username: registerForm.username,
      password: registerForm.password,
    });
    auth.setAuth(data.access_token, data.user);
    ElMessage.success("注册成功");
    router.push("/image");
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "注册失败");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  position: relative;
  min-height: 100%;
  padding: 34px 28px;
  overflow: hidden;
  box-sizing: border-box;
  color: #102033;
  background:
    radial-gradient(circle at 12% 18%, rgba(47, 140, 255, 0.15), transparent 30%),
    radial-gradient(circle at 82% 78%, rgba(34, 166, 168, 0.14), transparent 34%),
    linear-gradient(135deg, #f8fbff 0%, #eef5ff 50%, #f8f5ff 100%);
}

.bg-mesh,
.bg-grid,
.bg-glow {
  position: absolute;
  pointer-events: none;
}

.bg-mesh {
  inset: 0;
  background:
    linear-gradient(120deg, rgba(255, 255, 255, 0.62), transparent 36%),
    radial-gradient(circle at 60% 28%, rgba(125, 77, 255, 0.08), transparent 24%);
}

.bg-grid {
  inset: 0;
  background-image: linear-gradient(to right, rgba(86, 126, 255, 0.08) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(86, 126, 255, 0.08) 1px, transparent 1px);
  background-size: 36px 36px;
  opacity: 0.24;
}

.bg-glow {
  width: 560px;
  height: 560px;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.45;
}

.glow-left {
  left: -190px;
  top: -160px;
  background: radial-gradient(circle, rgba(47, 140, 255, 0.46), rgba(47, 140, 255, 0));
}

.glow-right {
  right: -170px;
  bottom: -220px;
  background: radial-gradient(circle, rgba(34, 166, 168, 0.42), rgba(34, 166, 168, 0));
}

.auth-shell {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: minmax(480px, 1.16fr) minmax(400px, 0.84fr);
  align-items: center;
  gap: 34px;
  max-width: 1240px;
  min-height: calc(100vh - 68px);
  margin: 0 auto;
}

.intro-panel {
  padding: 24px 4px;
}

.brand-pill,
.auth-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border: 1px solid rgba(82, 132, 255, 0.18);
  border-radius: 999px;
  color: #2f6ce5;
  background: rgba(255, 255, 255, 0.75);
  box-shadow: 0 10px 28px rgba(53, 94, 203, 0.08);
  font-size: 13px;
  font-weight: 800;
}

.intro-title {
  max-width: 760px;
  margin: 22px 0 14px;
  color: #102033;
  font-size: 44px;
  line-height: 1.16;
  letter-spacing: -0.5px;
}

.intro-subtitle {
  max-width: 720px;
  margin: 0;
  color: #61728c;
  font-size: 15px;
  line-height: 1.9;
}

.capability-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  max-width: 640px;
  margin-top: 24px;
}

.capability-card {
  min-height: 92px;
  padding: 16px;
  border: 1px solid #e3ecfb;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 14px 34px rgba(64, 97, 150, 0.08);
}

.capability-card span {
  display: block;
  color: #12233a;
  font-size: 28px;
  font-weight: 900;
}

.capability-card p {
  margin: 8px 0 0;
  color: #22a6a8;
  font-size: 13px;
  font-weight: 800;
}

.feature-list {
  display: grid;
  gap: 14px;
  max-width: 720px;
  margin-top: 18px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px;
  border: 1px solid rgba(218, 229, 248, 0.92);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.76);
  box-shadow: 0 14px 34px rgba(64, 97, 150, 0.07);
  backdrop-filter: blur(8px);
}

.feature-icon {
  display: grid;
  place-items: center;
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  color: #2f6ce5;
  border-radius: 16px;
  background: #eef5ff;
  font-size: 20px;
}

.feature-item h3 {
  margin: 0;
  color: #1c2e45;
  font-size: 15px;
}

.feature-item p {
  margin: 6px 0 0;
  color: #6d7f98;
  font-size: 13px;
  line-height: 1.65;
}

.flow-card {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  max-width: 720px;
  margin-top: 18px;
  padding: 14px 16px;
  border: 1px solid rgba(218, 229, 248, 0.92);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.62);
}

.flow-card span {
  color: #2f6ce5;
  font-size: 13px;
  font-weight: 900;
}

.flow-card i {
  width: 28px;
  height: 1px;
  background: linear-gradient(90deg, #8fb1ff, transparent);
}

.auth-panel {
  display: flex;
  justify-content: center;
}

.auth-card {
  width: 100%;
  border: 1px solid rgba(218, 229, 248, 0.95);
  border-radius: 30px;
  background:
    radial-gradient(circle at 86% 14%, rgba(47, 140, 255, 0.1), transparent 26%),
    rgba(255, 255, 255, 0.9);
  box-shadow: 0 24px 62px rgba(54, 87, 140, 0.16);
  backdrop-filter: blur(14px);
  overflow: hidden;
}

:deep(.el-card__body) {
  padding: 30px;
}

.auth-badge {
  margin-bottom: 16px;
  color: #22a6a8;
}

.card-header h2 {
  margin: 0;
  color: #102033;
  font-size: 28px;
  line-height: 1.25;
}

.card-header p {
  margin: 9px 0 0;
  color: #667894;
  font-size: 14px;
  line-height: 1.75;
}

.auth-tabs {
  margin-top: 20px;
}

:deep(.auth-tabs .el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.auth-tabs .el-tabs__nav-wrap::after) {
  height: 1px;
  background: #edf2fb;
}

:deep(.auth-tabs .el-tabs__active-bar) {
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, #2f8cff 0%, #7d4dff 100%);
}

:deep(.auth-tabs .el-tabs__item) {
  height: 44px;
  color: #6a7898;
  font-weight: 800;
}

:deep(.auth-tabs .el-tabs__item.is-active) {
  color: #2f6ce5;
}

.auth-form {
  margin-top: 4px;
}

:deep(.auth-form .el-form-item) {
  margin-bottom: 18px;
}

:deep(.auth-form .el-form-item__label) {
  color: #4f5f7f;
  font-size: 13px;
  font-weight: 700;
  padding-bottom: 7px;
}

:deep(.auth-form .el-input__wrapper) {
  border-radius: 14px;
  box-shadow: 0 0 0 1px #dfe9fb inset;
  padding: 2px 13px;
  background: #fbfdff;
  transition: box-shadow 0.22s ease, background 0.22s ease;
}

:deep(.auth-form .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #bfd4f7 inset;
}

:deep(.auth-form .el-input__wrapper.is-focus) {
  background: #fff;
  box-shadow: 0 0 0 1px #4f7fff inset, 0 0 0 4px rgba(78, 126, 255, 0.12);
}

:deep(.auth-form .el-input__prefix-inner) {
  color: #7f90b6;
}

.submit-btn {
  width: 100%;
  height: 48px;
  margin-top: 4px;
  border: 0;
  border-radius: 14px;
  font-weight: 800;
  letter-spacing: 0.2px;
  background: linear-gradient(135deg, #2f8cff 0%, #7d4dff 100%);
  box-shadow: 0 14px 30px rgba(77, 132, 255, 0.3);
}

.submit-btn:hover {
  transform: translateY(-1px);
}

.auth-tips {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid #edf2fb;
}

.auth-tips span {
  color: #7a8ba4;
  font-size: 12px;
}

.auth-tips b {
  padding: 6px 10px;
  color: #2f6ce5;
  border-radius: 999px;
  background: #f0f6ff;
  font-size: 12px;
}

@media (max-width: 1100px) {
  .auth-page {
    overflow: auto;
  }
  .auth-shell {
    grid-template-columns: 1fr;
    min-height: auto;
  }
  .intro-panel {
    padding-top: 6px;
  }
}

@media (max-width: 720px) {
  .auth-page {
    padding: 22px 16px;
  }
  .intro-title {
    font-size: 30px;
  }
  .capability-grid {
    grid-template-columns: 1fr;
  }
  :deep(.el-card__body) {
    padding: 24px;
  }
}
</style>
