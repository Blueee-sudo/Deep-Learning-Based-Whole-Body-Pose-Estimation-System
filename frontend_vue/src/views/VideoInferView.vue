<template>
  <section class="video-infer-page">
    <div class="hero-card">
      <div class="hero-content">
        <el-tag class="hero-tag" effect="light">Video Pose Pipeline</el-tag>
        <h1>视频姿态推理</h1>
        <p>上传人体动作视频，系统将按抽帧策略完成姿态关键点检测、可视化渲染与结果视频生成</p>
      </div>
      <div class="hero-flow-card">
        <div class="flow-card-title">视频检测流程</div>
        <div class="flow-steps">
          <span>上传视频</span>
          <i></i>
          <span>抽帧推理</span>
          <i></i>
          <span>生成结果</span>
        </div>
        <div class="flow-note">适合动作过程回放、离线视频分析与检测结果留存</div>
      </div>
    </div>

    <div class="overview-grid">
      <div class="overview-card">
        <div class="overview-label">处理模式</div>
        <div class="overview-value">Video / MP4</div>
        <div class="overview-trend">离线异步处理</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">抽帧间隔</div>
        <div class="overview-value">每 {{ frameStride }} 帧</div>
        <div class="overview-trend">{{ strideHint }}</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">任务状态</div>
        <div class="overview-value">{{ statusLabel }}</div>
        <div class="overview-trend">{{ task.detection_id ? `任务 #${task.detection_id}` : "等待上传" }}</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">处理进度</div>
        <div class="overview-value">{{ progressPercent }}%</div>
        <div class="overview-trend">已处理 {{ task.processed_frames || 0 }} / {{ task.total_frames || "?" }} 帧</div>
      </div>
    </div>

    <div class="operation-grid">
      <div class="panel-card upload-panel">
        <div class="section-heading">
          <div>
            <h2>上传与处理配置</h2>
            <p>选择视频文件并设置抽帧间隔，间隔越小精度越高、耗时越长</p>
          </div>
          <el-tag :type="result ? 'success' : loading ? 'warning' : 'info'" effect="light">{{ statusLabel }}</el-tag>
        </div>

        <el-upload class="upload-box" drag :auto-upload="false" :limit="1" :on-change="onFileChange">
          <div class="upload-inner">
            <div class="upload-icon">
              <el-icon><UploadFilled /></el-icon>
            </div>
            <div class="upload-title">拖拽视频到此处，或点击上传</div>
            <div class="upload-desc">建议使用 MP4 / H264 视频，画面中人体尽量完整且动作过程清晰</div>
            <div v-if="file" class="file-chip">已选择：{{ file.name }}</div>
          </div>
        </el-upload>

        <div class="config-block">
          <div class="config-label">抽帧间隔（每几帧推一次）</div>
          <el-select v-model="frameStride" class="stride-select">
            <el-option v-for="item in strideOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
          <div class="config-tip">{{ strideHint }}</div>
        </div>

        <div class="action-buttons">
          <el-button class="primary-gradient-btn" type="primary" :loading="loading" @click="onInfer">开始处理</el-button>
          <el-button v-if="result" class="ghost-btn" @click="onDownload">下载结果视频</el-button>
        </div>
      </div>

      <div class="panel-card guide-panel">
        <div class="section-heading">
          <div>
            <h2>检测流程 / 使用提示</h2>
            <p>视频任务会在后台持续处理，请等待进度完成后下载结果</p>
          </div>
        </div>
        <div class="process-line">
          <div class="process-step">上传视频</div>
          <div class="process-arrow">→</div>
          <div class="process-step">读取帧</div>
          <div class="process-arrow">→</div>
          <div class="process-step">姿态推理</div>
          <div class="process-arrow">→</div>
          <div class="process-step">骨架绘制</div>
          <div class="process-arrow">→</div>
          <div class="process-step">导出视频</div>
        </div>
        <div class="tips-card">
          <div class="tips-title">视频建议</div>
          <ul>
            <li>建议上传光照清晰、人物完整的视频片段</li>
            <li>视频越长处理时间越久，可优先使用短片段测试</li>
            <li>CPU 模式下推荐每 2 或 3 帧推理一次，兼顾速度与效果</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="status-section">
      <div class="progress-panel">
        <div class="panel-title">任务进度</div>
        <div class="progress-body">
          <div class="progress-header">
            <div>
              <div class="progress-title">{{ task.detection_id ? `检测任务 #${task.detection_id}` : "暂无任务" }}</div>
              <div class="progress-subtitle">
                已推理 {{ task.inferred_frames || 0 }} 帧，已处理 {{ task.processed_frames || 0 }} / {{ task.total_frames || "?" }} 帧
              </div>
            </div>
            <el-tag :type="result ? 'success' : loading ? 'warning' : 'info'" effect="light">{{ statusLabel }}</el-tag>
          </div>
          <el-progress
            :percentage="progressPercent"
            :indeterminate="task.total_frames === 0 && task.status === 'processing'"
            :duration="2"
            :stroke-width="18"
          />
          <div class="progress-meta">
            <span>抽帧间隔：每 {{ task.frame_stride || frameStride }} 帧</span>
            <span>总帧数：{{ task.total_frames || "待获取" }}</span>
          </div>
        </div>
      </div>

      <div class="result-panel">
        <div class="panel-title">处理结果</div>
        <div v-if="result" class="result-body">
          <div class="result-badge">DONE</div>
          <div class="result-title">结果视频已生成</div>
          <div class="result-desc">记录ID：{{ result.detection_id }}，已处理 {{ result.processed_frames }} / {{ result.total_frames }} 帧</div>
          <el-button class="primary-gradient-btn" type="primary" @click="onDownload">下载结果视频</el-button>
        </div>
        <div v-else class="empty-result">
          <div class="empty-icon">MP4</div>
          <div>{{ loading ? "视频处理中，请稍候..." : "任务完成后将在这里提供下载入口" }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import { ElMessage } from "element-plus";
import { UploadFilled } from "@element-plus/icons-vue";
import { downloadVideoResult, getVideoProgress, inferVideo } from "../api/pose";

const file = ref(null);
const loading = ref(false);
const result = ref(null);
const task = ref({
  detection_id: null,
  status: "",
  total_frames: 0,
  processed_frames: 0,
  inferred_frames: 0,
  frame_stride: 1,
  progress_percent: 0,
});
const frameStride = ref(2);
let pollTimer = null;
const strideOptions = [
  { label: "1 帧（最准确，最慢）", value: 1 },
  { label: "2 帧（推荐）", value: 2 },
  { label: "3 帧（更快）", value: 3 },
  { label: "4 帧（最快，精度更低）", value: 4 },
];
const progressPercent = computed(() => Math.max(0, Math.min(Number(task.value.progress_percent || 0), 100)));
const statusLabel = computed(() => {
  if (result.value) return "已完成";
  if (loading.value || task.value.status === "processing") return "处理中";
  if (task.value.status === "failed") return "处理失败";
  if (file.value) return "待处理";
  return "待上传";
});
const strideHint = computed(() => {
  if (frameStride.value === 1) return "最准确，处理速度较慢";
  if (frameStride.value === 2) return "推荐设置，兼顾效果和速度";
  if (frameStride.value === 3) return "更快处理，适合较长视频";
  return "最快处理，精度相对降低";
});

function onFileChange(uploadFile) {
  file.value = uploadFile.raw;
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

async function pollProgress(detectionId) {
  const data = await getVideoProgress(detectionId);
  task.value = { ...task.value, ...data };

  if (data.status === "done") {
    stopPolling();
    loading.value = false;
    result.value = {
      detection_id: data.detection_id,
      frame_stride: data.frame_stride,
      total_frames: data.total_frames,
      processed_frames: data.processed_frames,
    };
    ElMessage.success("视频处理完成");
  } else if (data.status === "failed") {
    stopPolling();
    loading.value = false;
    ElMessage.error(data.error_msg || "视频处理失败");
  }
}

async function onInfer() {
  if (!file.value) {
    ElMessage.warning("请先选择视频");
    return;
  }
  stopPolling();
  loading.value = true;
  result.value = null;
  task.value = {
    detection_id: null,
    status: "processing",
    total_frames: 0,
    processed_frames: 0,
    inferred_frames: 0,
    frame_stride: frameStride.value,
    progress_percent: 0,
  };
  ElMessage.info(`视频处理中（每 ${frameStride.value} 帧推一次），CPU 模式可能耗时较久，请耐心等待`);
  try {
    const fd = new FormData();
    fd.append("file", file.value);
    fd.append("frame_stride", String(frameStride.value));
    const data = await inferVideo(fd);
    task.value = { ...task.value, ...data };
    if (data?.detection_id) {
      await pollProgress(data.detection_id);
      pollTimer = setInterval(() => {
        pollProgress(data.detection_id).catch(() => {});
      }, 1000);
    } else {
      loading.value = false;
      ElMessage.error("未获取到任务ID");
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "视频处理失败");
    loading.value = false;
  }
}

async function onDownload() {
  if (!result.value?.detection_id) return;
  try {
    const resp = await downloadVideoResult(result.value.detection_id);
    const blob = resp.data;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `pose_${result.value.detection_id}.mp4`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "下载失败，请稍后重试");
  }
}

onBeforeUnmount(() => {
  stopPolling();
});
</script>

<style scoped>
.video-infer-page {
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
.operation-grid,
.status-section {
  display: grid;
  grid-template-columns: minmax(420px, 1.05fr) minmax(360px, 0.95fr);
  gap: 18px;
  align-items: stretch;
}
.panel-card,
.progress-panel,
.result-panel {
  border: 1px solid #e3ecfb;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 42px rgba(64, 97, 150, 0.08);
  overflow: hidden;
}
.panel-card {
  padding: 20px;
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
.upload-box {
  width: 100%;
}
.upload-box :deep(.el-upload) {
  width: 100%;
}
.upload-box :deep(.el-upload-dragger) {
  width: 100%;
  min-height: 204px;
  padding: 30px 20px;
  border: 1.5px dashed #a9c7ff;
  border-radius: 22px;
  background:
    radial-gradient(circle at 50% 0%, rgba(57, 134, 255, 0.11), transparent 55%),
    linear-gradient(180deg, #fbfdff 0%, #f4f8ff 100%);
  transition: all 0.2s ease;
}
.upload-box :deep(.el-upload-dragger:hover) {
  border-color: #5b8cff;
  box-shadow: 0 16px 32px rgba(75, 132, 230, 0.12);
}
.upload-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 140px;
  text-align: center;
}
.upload-icon {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  color: #fff;
  border-radius: 20px;
  background: linear-gradient(135deg, #2f8cff 0%, #7d4dff 100%);
  box-shadow: 0 14px 28px rgba(77, 132, 255, 0.28);
  font-size: 26px;
}
.upload-title {
  color: #1c2e45;
  font-size: 15px;
  font-weight: 800;
}
.upload-desc,
.config-tip {
  color: #7b8da6;
  font-size: 12px;
  line-height: 1.6;
}
.file-chip {
  max-width: 100%;
  padding: 6px 10px;
  color: #2f6ce5;
  border-radius: 999px;
  background: #eef5ff;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.config-block {
  margin-top: 18px;
}
.config-label {
  margin-bottom: 10px;
  color: #44566e;
  font-size: 13px;
  font-weight: 700;
}
.stride-select {
  width: 100%;
}
.config-tip {
  margin-top: 8px;
}
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
}
.primary-gradient-btn {
  min-width: 148px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #2f8cff 0%, #7d4dff 100%);
  box-shadow: 0 14px 28px rgba(77, 132, 255, 0.26);
}
.ghost-btn {
  min-width: 132px;
  border-color: #dfe8f8;
  border-radius: 14px;
  color: #37506f;
  background: #fff;
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
.panel-title {
  display: flex;
  align-items: center;
  min-height: 48px;
  padding: 0 18px;
  color: #20324a;
  font-size: 14px;
  font-weight: 800;
  border-bottom: 1px solid #edf2fb;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}
.progress-body,
.result-body,
.empty-result {
  padding: 20px;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}
.progress-title {
  color: #1c2e45;
  font-size: 18px;
  font-weight: 900;
}
.progress-subtitle,
.result-desc {
  margin-top: 6px;
  color: #73859e;
  font-size: 13px;
}
.progress-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 14px;
  color: #60728b;
  font-size: 12px;
}
.result-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.result-badge {
  width: max-content;
  padding: 7px 11px;
  color: #0f9f6e;
  border-radius: 999px;
  background: #eafaf4;
  font-size: 12px;
  font-weight: 900;
}
.result-title {
  color: #1c2e45;
  font-size: 19px;
  font-weight: 900;
}
.empty-result {
  min-height: 178px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #8a9bb3;
  text-align: center;
}
.empty-icon {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  color: #6d8ee8;
  font-size: 13px;
  font-weight: 900;
  border-radius: 20px;
  background: #eef5ff;
}

@media (max-width: 1366px) {
  .hero-card {
    padding: 24px;
  }
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 992px) {
  .hero-card,
  .operation-grid,
  .status-section {
    grid-template-columns: 1fr;
  }
  .hero-card {
    flex-direction: column;
  }
  .hero-flow-card {
    width: auto;
    align-self: stretch;
  }
}

@media (max-width: 640px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
  .hero-content h1 {
    font-size: 26px;
  }
  .action-buttons {
    flex-direction: column;
  }
  .primary-gradient-btn,
  .ghost-btn {
    width: 100%;
  }
}
</style>
