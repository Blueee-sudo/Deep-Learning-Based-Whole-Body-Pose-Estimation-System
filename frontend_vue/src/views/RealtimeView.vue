<template>
  <section class="realtime-page">
    <div class="hero-card">
      <div class="hero-content">
        <el-tag class="hero-tag" effect="light">Realtime Pose Stream</el-tag>
        <h1>实时帧检测</h1>
        <p>调用本地摄像头采集视频帧，系统将实时完成姿态关键点定位与主骨架可视化叠加</p>
      </div>
      <div class="hero-flow-card">
        <div class="flow-card-title">实时检测链路</div>
        <div class="flow-steps">
          <span>摄像头</span>
          <i></i>
          <span>帧采样</span>
          <i></i>
          <span>骨架叠加</span>
        </div>
        <div class="flow-note">WebSocket 优先，异常时自动回退 HTTP 推理</div>
      </div>
    </div>

    <div class="overview-grid">
      <div class="overview-card">
        <div class="overview-label">运行状态</div>
        <div class="overview-value">{{ realtimeStatusLabel }}</div>
        <div class="overview-trend">摄像头实时采集</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">通信模式</div>
        <div class="overview-value">{{ modeLabel }}</div>
        <div class="overview-trend">WebSocket 优先</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">检测人数</div>
        <div class="overview-value">{{ personCount }}</div>
        <div class="overview-trend">主骨架实时叠加</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">推理耗时</div>
        <div class="overview-value">{{ inferMs }} ms</div>
        <div class="overview-trend">约 600ms 采样一次</div>
      </div>
    </div>

    <div class="realtime-grid">
      <div class="stage-panel">
        <div class="panel-title">
          <span>实时画面 / 关键点叠加</span>
          <el-tag :type="mode === 'idle' ? 'info' : 'success'" effect="light">{{ realtimeStatusLabel }}</el-tag>
        </div>
        <div class="stage-wrap">
          <div class="video-stage" ref="stageRef">
            <video ref="videoRef" autoplay muted playsinline class="video-el"></video>
            <canvas ref="overlayRef" class="overlay-canvas"></canvas>
            <div v-if="mode === 'idle'" class="stage-placeholder">
              <div class="empty-icon">CAM</div>
              <div>点击“启动摄像头”开始实时检测</div>
            </div>
          </div>
        </div>
        <div class="toolbar">
          <el-button class="primary-gradient-btn" type="primary" @click="start">启动摄像头</el-button>
          <el-button class="ghost-btn" type="warning" @click="stop">停止检测</el-button>
        </div>
      </div>

      <div class="side-stack">
        <div class="panel-card">
          <div class="section-heading">
            <div>
              <h2>检测状态</h2>
              <p>实时展示当前推理链路和检测结果摘要</p>
            </div>
            <el-tag :type="mode === 'websocket' ? 'success' : mode === 'http' ? 'warning' : 'info'" effect="light">
              {{ modeLabel }}
            </el-tag>
          </div>
          <div class="analysis-list">
            <div class="analysis-row">
              <span>当前通信模式</span>
              <b>{{ modeLabel }}</b>
            </div>
            <div class="analysis-row">
              <span>检测人数</span>
              <b>{{ personCount }}</b>
            </div>
            <div class="analysis-row">
              <span>推理耗时</span>
              <b>{{ inferMs }} ms</b>
            </div>
            <div class="analysis-row">
              <span>显示内容</span>
              <b>body + foot</b>
            </div>
            <div class="analysis-row">
              <span>手脸细粒度</span>
              <b>默认关闭</b>
            </div>
          </div>
        </div>

        <div class="panel-card guide-panel">
          <div class="section-heading">
            <div>
              <h2>实时检测提示</h2>
              <p>保持人物完整入镜可获得更稳定的实时骨架</p>
            </div>
          </div>
          <div class="process-line">
            <div class="process-step">启动摄像头</div>
            <div class="process-arrow">→</div>
            <div class="process-step">采集帧</div>
            <div class="process-arrow">→</div>
            <div class="process-step">姿态推理</div>
            <div class="process-arrow">→</div>
            <div class="process-step">画布叠加</div>
          </div>
          <div class="tips-card">
            <div class="tips-title">使用建议</div>
            <ul>
              <li>确保浏览器允许摄像头权限</li>
              <li>保持光照充足，人物尽量位于画面中央</li>
              <li>如 WebSocket 不可用，系统会自动使用 HTTP 回退模式</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import { inferRealtimeFrame } from "../api/pose";
import { drawRealtimePose } from "../utils/poseDraw";

const stageRef = ref(null);
const videoRef = ref(null);
const overlayRef = ref(null);
let stream = null;
let timer = null;
let ws = null;
let stageResizeObserver = null;
const personCount = ref(0);
const inferMs = ref(0);
const mode = ref("idle");
const modeLabel = computed(() => {
  if (mode.value === "websocket") return "WebSocket";
  if (mode.value === "http") return "HTTP";
  return "Idle";
});
const realtimeStatusLabel = computed(() => (mode.value === "idle" ? "待启动" : "检测中"));

function frameToBase64(video) {
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.8).split(",")[1];
}

function syncOverlaySize() {
  const video = videoRef.value;
  const overlay = overlayRef.value;
  const stage = stageRef.value;
  if (!video || !overlay || !stage) return;
  const rect = video.getBoundingClientRect();
  if (!rect.width || !rect.height) return;
  overlay.width = Math.round(rect.width);
  overlay.height = Math.round(rect.height);
  overlay.style.width = `${Math.round(rect.width)}px`;
  overlay.style.height = `${Math.round(rect.height)}px`;
  stage.style.width = `${Math.round(rect.width)}px`;
}

function drawPersons(persons, imageSize) {
  const overlay = overlayRef.value;
  if (!overlay) return;
  const ctx = overlay.getContext("2d");
  if (!ctx) return;
  const srcW = imageSize?.width || videoRef.value?.videoWidth || overlay.width || 1;
  const srcH = imageSize?.height || videoRef.value?.videoHeight || overlay.height || 1;
  const scaleX = overlay.width / srcW;
  const scaleY = overlay.height / srcH;
  drawRealtimePose(ctx, persons || [], { scaleX, scaleY, minScore: 0.2, withBbox: true, withFaceHands: false });
}

function clearOverlay() {
  const overlay = overlayRef.value;
  if (!overlay) return;
  const ctx = overlay.getContext("2d");
  if (!ctx) return;
  ctx.clearRect(0, 0, overlay.width, overlay.height);
}

function applyResult(res) {
  personCount.value = res?.persons?.length || 0;
  inferMs.value = res?.inference_time_ms || 0;
  drawPersons(res?.persons || [], res?.image_size);
}

async function tick() {
  if (!videoRef.value) return;
  const frame = frameToBase64(videoRef.value);
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ frame }));
    return;
  }
  const res = await inferRealtimeFrame(frame); // fallback http
  applyResult(res);
  mode.value = "http";
}

async function start() {
  if (stream) {
    stop();
  }
  stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
  videoRef.value.srcObject = stream;
  videoRef.value.onloadedmetadata = () => {
    syncOverlaySize();
  };

  if (!stageResizeObserver && stageRef.value) {
    stageResizeObserver = new ResizeObserver(() => syncOverlaySize());
    stageResizeObserver.observe(stageRef.value);
  }
  window.removeEventListener("resize", syncOverlaySize);
  window.addEventListener("resize", syncOverlaySize);

  const protocol = location.protocol === "https:" ? "wss" : "ws";
  try {
    ws = new WebSocket(`${protocol}://${location.host}/ws/pose/realtime/`);
    ws.onopen = () => {
      mode.value = "websocket";
    };
    ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);
        applyResult(data);
      } catch {}
    };
    ws.onerror = () => {
      mode.value = "http";
    };
    ws.onclose = () => {
      if (mode.value !== "http") mode.value = "http";
    };
  } catch {
    mode.value = "http";
  }
  if (timer) clearInterval(timer);
  timer = setInterval(() => {
    tick().catch(() => {});
  }, 600);
}

function stop() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
  if (stream) {
    stream.getTracks().forEach((t) => t.stop());
    stream = null;
  }
  if (ws) {
    ws.close();
    ws = null;
  }
  clearOverlay();
  personCount.value = 0;
  inferMs.value = 0;
  mode.value = "idle";
}

onBeforeUnmount(() => {
  stop();
  window.removeEventListener("resize", syncOverlaySize);
  if (stageResizeObserver) {
    stageResizeObserver.disconnect();
    stageResizeObserver = null;
  }
});
</script>

<style scoped>
.realtime-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
  color: #102033;
}
.hero-card {
  position: relative;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  min-height: 168px;
  padding: 28px;
  overflow: hidden;
  border: 1px solid rgba(214, 226, 248, 0.9);
  border-radius: 26px;
  background:
    radial-gradient(circle at 84% 22%, rgba(103, 147, 255, 0.24), transparent 28%),
    linear-gradient(135deg, #f7fbff 0%, #edf5ff 48%, #f7f4ff 100%);
  box-shadow: 0 20px 48px rgba(60, 93, 148, 0.12);
}
.hero-card::after {
  content: "";
  position: absolute;
  right: -80px;
  top: -120px;
  width: 320px;
  height: 320px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(47, 140, 255, 0.22), transparent 68%);
}
.hero-content,
.hero-flow-card {
  position: relative;
  z-index: 1;
}
.hero-tag {
  margin-bottom: 14px;
  border-color: rgba(82, 132, 255, 0.18);
  color: #2f6ce5;
  background: rgba(255, 255, 255, 0.72);
}
.hero-content h1 {
  margin: 0;
  color: #102033;
  font-size: 32px;
  line-height: 1.15;
  letter-spacing: 0.4px;
}
.hero-content p {
  max-width: 650px;
  margin: 12px 0 0;
  color: #667894;
  font-size: 15px;
  line-height: 1.8;
}
.hero-flow-card {
  align-self: center;
  width: 360px;
  padding: 18px;
  border: 1px solid rgba(220, 230, 247, 0.92);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 16px 36px rgba(70, 107, 160, 0.1);
  backdrop-filter: blur(10px);
}
.flow-card-title {
  color: #20324a;
  font-size: 14px;
  font-weight: 700;
}
.flow-steps {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  color: #2f6ce5;
  font-size: 12px;
  font-weight: 700;
}
.flow-steps span {
  padding: 7px 9px;
  border-radius: 999px;
  background: #eef5ff;
}
.flow-steps i {
  flex: 1;
  height: 1px;
  min-width: 12px;
  background: linear-gradient(90deg, #9fc1ff, transparent);
}
.flow-note {
  margin-top: 14px;
  color: #7a8ba4;
  font-size: 12px;
}
.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}
.overview-card {
  min-height: 104px;
  padding: 18px;
  border: 1px solid #e3ecfb;
  border-radius: 22px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: 0 14px 34px rgba(64, 97, 150, 0.08);
}
.overview-label {
  color: #75879f;
  font-size: 12px;
}
.overview-value {
  margin-top: 10px;
  color: #12233a;
  font-size: 22px;
  font-weight: 800;
}
.overview-trend {
  margin-top: 8px;
  color: #22a6a8;
  font-size: 12px;
}
.realtime-grid {
  display: grid;
  grid-template-columns: minmax(560px, 1.35fr) minmax(340px, 0.65fr);
  gap: 18px;
  align-items: stretch;
}
.stage-panel,
.panel-card {
  border: 1px solid #e3ecfb;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 42px rgba(64, 97, 150, 0.08);
  overflow: hidden;
}
.panel-card {
  padding: 20px;
}
.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 54px;
  padding: 0 18px;
  color: #20324a;
  font-size: 14px;
  font-weight: 800;
  border-bottom: 1px solid #edf2fb;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}
.stage-wrap {
  padding: 18px;
  background: #f7faff;
}
.video-stage {
  position: relative;
  display: block;
  max-width: 100%;
  min-height: 420px;
  margin: 0 auto;
  border: 1px solid #dfe8f8;
  border-radius: 22px;
  overflow: hidden;
  background: #0f172a;
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.18);
}
.video-el {
  display: block;
  width: 100%;
  max-width: 100%;
  min-height: 420px;
  object-fit: cover;
}
.overlay-canvas {
  position: absolute;
  left: 0;
  top: 0;
  pointer-events: none;
}
.stage-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #dbeafe;
  text-align: center;
  background:
    radial-gradient(circle at 50% 30%, rgba(47, 140, 255, 0.18), transparent 38%),
    rgba(15, 23, 42, 0.92);
}
.empty-icon {
  display: grid;
  place-items: center;
  width: 62px;
  height: 62px;
  color: #93c5fd;
  font-size: 13px;
  font-weight: 900;
  border-radius: 22px;
  background: rgba(59, 130, 246, 0.16);
  border: 1px solid rgba(147, 197, 253, 0.2);
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  padding: 0 18px 18px;
}
.primary-gradient-btn {
  min-width: 148px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #2f8cff 0%, #7d4dff 100%);
  box-shadow: 0 14px 28px rgba(77, 132, 255, 0.26);
}
.ghost-btn {
  min-width: 118px;
  border-color: #dfe8f8;
  border-radius: 14px;
  color: #37506f;
  background: #fff;
}
.side-stack {
  display: grid;
  gap: 18px;
}
.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.section-heading h2 {
  margin: 0;
  color: #1c2e45;
  font-size: 17px;
}
.section-heading p {
  margin: 6px 0 0;
  color: #73859e;
  font-size: 13px;
}
.analysis-list {
  padding-top: 2px;
}
.analysis-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px dashed #e5edf8;
  color: #73859e;
  font-size: 13px;
}
.analysis-row:last-child {
  border-bottom: 0;
}
.analysis-row b {
  color: #20324a;
  font-weight: 800;
}
.process-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  padding: 16px;
  border: 1px solid #e7effc;
  border-radius: 20px;
  background: linear-gradient(180deg, #fbfdff 0%, #f6f9ff 100%);
}
.process-step {
  padding: 9px 12px;
  color: #2f6ce5;
  font-size: 12px;
  font-weight: 800;
  border-radius: 999px;
  background: #eef5ff;
}
.process-arrow {
  color: #9aaec8;
  font-weight: 800;
}
.tips-card {
  margin-top: 16px;
  padding: 18px;
  border-radius: 20px;
  background:
    radial-gradient(circle at 100% 0%, rgba(37, 209, 215, 0.13), transparent 36%),
    #f8fbff;
}
.tips-title {
  color: #20324a;
  font-weight: 800;
}
.tips-card ul {
  margin: 12px 0 0;
  padding-left: 18px;
  color: #60728b;
  line-height: 1.9;
  font-size: 13px;
}

@media (max-width: 1366px) {
  .hero-card {
    padding: 24px;
  }
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .realtime-grid {
    grid-template-columns: 1fr;
  }
  .side-stack {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 992px) {
  .hero-card {
    flex-direction: column;
  }
  .hero-flow-card {
    width: auto;
    align-self: stretch;
  }
  .side-stack {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
  .hero-content h1 {
    font-size: 26px;
  }
  .toolbar {
    flex-direction: column;
  }
  .primary-gradient-btn,
  .ghost-btn {
    width: 100%;
  }
}
</style>
