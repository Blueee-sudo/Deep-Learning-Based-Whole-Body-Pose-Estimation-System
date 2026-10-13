<template>
  <section class="image-infer-page">
    <div class="hero-card">
      <div class="hero-content">
        <el-tag class="hero-tag" effect="light">AI Pose Estimation</el-tag>
        <h1>图片姿态推理</h1>
        <p>上传人体图像，系统将自动完成全身关键点定位、动作识别与可视化分析</p>
      </div>
      <div class="hero-flow-card">
        <div class="flow-card-title">人体关键点检测流程</div>
        <div class="flow-steps">
          <span>上传图像</span>
          <i></i>
          <span>模型推理</span>
          <i></i>
          <span>动作分析</span>
        </div>
        <div class="flow-note">支持全身 133 keypoints 与多动作评分</div>
      </div>
    </div>

    <div class="overview-grid">
      <div class="overview-card">
        <div class="overview-label">当前模型</div>
        <div class="overview-value" :title="modelLabel">{{ result ? modelLabel : "RTMW / Pose Estimation" }}</div>
        <div class="overview-trend">全身姿态估计</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">支持关键点</div>
        <div class="overview-value">133</div>
        <div class="overview-trend">body / face / hands</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">当前动作</div>
        <div class="overview-value">{{ actionTypeLabel }}</div>
        <div class="overview-trend">动作类型可切换</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">检测状态</div>
        <div class="overview-value">{{ detectionStatusLabel }}</div>
        <div class="overview-trend">{{ result?.detection_id ? `检测ID ${result.detection_id}` : "等待任务" }}</div>
      </div>
    </div>

    <div class="operation-grid">
      <div class="panel-card upload-panel">
        <div class="section-heading">
          <div>
            <h2>上传与参数配置</h2>
            <p>选择一张清晰的人体动作图片并配置动作类型</p>
          </div>
          <el-tag type="primary" effect="light">{{ actionTypeLabel }}</el-tag>
        </div>

        <el-upload
          v-if="!result"
          class="upload-box"
          drag
          :auto-upload="false"
          :show-file-list="true"
          :limit="1"
          :on-change="onFileChange"
        >
          <div class="upload-inner">
            <div class="upload-icon">
              <el-icon><UploadFilled /></el-icon>
            </div>
            <div class="upload-title">拖拽图片到此处，或点击上传</div>
            <div class="upload-desc">支持 JPG / PNG / JPEG，建议上传包含完整人体的清晰图片</div>
          </div>
        </el-upload>
        <div v-else class="upload-locked">
          <div class="upload-icon upload-icon--done">
            <el-icon><UploadFilled /></el-icon>
          </div>
          <div>
            <div class="upload-title">当前检测已完成</div>
            <div class="upload-desc">如需更换图片，请点击重新上传</div>
          </div>
        </div>

        <div v-if="!result" class="action-selector">
          <div class="action-label">动作类型</div>
          <el-radio-group v-model="selectedActionType" class="action-radio-group">
            <el-radio-button label="squat">深蹲</el-radio-button>
            <el-radio-button label="plank">平板支撑</el-radio-button>
            <el-radio-button label="pushup">俯卧撑</el-radio-button>
            <el-radio-button label="glute_bridge">臀桥</el-radio-button>
            <el-radio-button label="situp">仰卧起坐</el-radio-button>
          </el-radio-group>
        </div>

        <div class="action-buttons">
          <el-button v-if="!result" class="primary-gradient-btn" type="primary" :loading="loading" @click="onInfer">
            开始推理
          </el-button>
          <el-button v-else class="primary-gradient-btn" type="primary" @click="onReset">重新上传</el-button>
          <el-button v-if="!result" class="ghost-btn" @click="onReset">重置</el-button>
          <el-button v-if="result?.detection_id" class="ghost-btn" @click="onDownloadResult">下载结果图</el-button>
        </div>
      </div>

      <div class="panel-card guide-panel">
        <div class="section-heading">
          <div>
            <h2>检测流程 / 使用提示</h2>
            <p>上传后系统会自动完成端到端姿态分析</p>
          </div>
        </div>
        <div class="process-line">
          <div class="process-step">上传图像</div>
          <div class="process-arrow">→</div>
          <div class="process-step">模型推理</div>
          <div class="process-arrow">→</div>
          <div class="process-step">关键点定位</div>
          <div class="process-arrow">→</div>
          <div class="process-step">动作分析</div>
          <div class="process-arrow">→</div>
          <div class="process-step">结果生成</div>
        </div>
        <div class="tips-card">
          <div class="tips-title">图片建议</div>
          <ul>
            <li>人物身体尽量完整，避免关键部位被遮挡</li>
            <li>保持光照清晰，背景不要过度复杂</li>
            <li>动作姿态明显，便于系统进行稳定评分</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="result-section">
      <div class="image-panel">
        <div class="panel-title">原始图像</div>
        <div class="image-canvas">
          <img v-if="sourceImageUrl" :src="sourceImageUrl" alt="source" />
          <div v-else class="placeholder">
            <div class="placeholder-icon">IMG</div>
            <div>上传后将在这里显示原图</div>
          </div>
        </div>
      </div>
      <div class="image-panel" v-loading="loading">
        <div class="panel-title">检测结果图像</div>
        <div class="image-canvas">
          <img v-if="result?.annotated_image" :src="result.annotated_image" alt="annotated" />
          <div v-else class="placeholder">
            <div class="placeholder-icon">AI</div>
            <div>{{ loading ? "模型推理中..." : "推理完成后将在这里显示结果图" }}</div>
          </div>
        </div>
      </div>
      <div class="analysis-panel">
        <div class="panel-title">分析结果</div>
        <div class="analysis-list">
          <div class="analysis-row">
            <span>动作类型</span>
            <b>{{ actionTypeLabel }}</b>
          </div>
          <div class="analysis-row">
            <span>检测状态</span>
            <el-tag :type="result ? 'success' : loading ? 'warning' : 'info'" effect="light">{{ detectionStatusLabel }}</el-tag>
          </div>
          <div class="analysis-row">
            <span>推理耗时</span>
            <b>{{ result?.inference_time_ms ? `${result.inference_time_ms} ms` : "-" }}</b>
          </div>
          <div class="analysis-row">
            <span>平均置信度</span>
            <b>{{ result ? averageConfidence : "-" }}</b>
          </div>
          <div class="analysis-row">
            <span>关键点数量</span>
            <b>{{ result ? `${detectedKeypoints} / ${totalKeypoints || 133}` : "133" }}</b>
          </div>
          <div class="analysis-row">
            <span>检测人数</span>
            <b>{{ result ? personsCount : "-" }}</b>
          </div>
        </div>

        <div class="score-card">
          <div class="score-header">
            <span>姿态评价</span>
            <el-tag v-if="poseAnalysis" size="small" type="info">{{ actionTypeLabel }}</el-tag>
          </div>
          <template v-if="hasPoseData">
            <div class="score-main">
              <div class="score-block">
                <div class="score-label">评分</div>
                <div class="score-value">{{ scoreDisplay }}</div>
              </div>
              <div class="score-block">
                <div class="score-label">评分范围</div>
                <div class="score-value">{{ scoringScopeLabel }}</div>
              </div>
            </div>
            <div class="score-comment">{{ scoreComment }}</div>

            <div v-if="problemsList.length" class="score-list">
              <div class="score-list-title">主要问题</div>
              <ul>
                <li v-for="(item, idx) in problemsList" :key="`p-${idx}`">{{ item }}</li>
              </ul>
            </div>

            <div v-if="suggestionsList.length" class="score-list">
              <div class="score-list-title">改进建议</div>
              <ul>
                <li v-for="(item, idx) in suggestionsList" :key="`s-${idx}`">{{ item }}</li>
              </ul>
            </div>
          </template>
          <div v-else class="score-empty">等待检测结果</div>
        </div>
      </div>
    </div>

    <el-collapse v-if="result" class="detail-collapse">
        <el-collapse-item name="overview" title="检测摘要详情">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="图像尺寸">
              {{ result.image_size?.width || "-" }} × {{ result.image_size?.height || "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="检测人数">{{ personsCount }}</el-descriptions-item>
            <el-descriptions-item label="关键点总数">{{ totalKeypoints }}</el-descriptions-item>
            <el-descriptions-item label="有效关键点">{{ detectedKeypoints }}</el-descriptions-item>
            <el-descriptions-item label="平均置信度">{{ averageConfidence }}</el-descriptions-item>
            <el-descriptions-item label="多人检测">{{ isMultiPerson ? "是" : "否" }}</el-descriptions-item>
          </el-descriptions>
        </el-collapse-item>

        <el-collapse-item v-if="poseAnalysis" name="pose-analysis" title="姿态分析详情（角度 / 对称性 / 置信度）">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="动作类型">{{ actionTypeLabel }}</el-descriptions-item>
            <el-descriptions-item label="评分范围">{{ scoringScopeLabel }}</el-descriptions-item>
            <el-descriptions-item label="主目标选择">{{ poseAnalysis.main_person_selected ? "是" : "否" }}</el-descriptions-item>
            <el-descriptions-item label="可评分">{{ poseAnalysis?.validity?.enough_keypoints ? "是" : "否" }}</el-descriptions-item>
            <template v-if="isPlankAction">
              <el-descriptions-item label="髋角">{{ fmt1(poseAnalysis?.angles?.hip_angle) }}°</el-descriptions-item>
              <el-descriptions-item label="躯干倾角">{{ fmt1(poseAnalysis?.angles?.torso_lean) }}°</el-descriptions-item>
              <el-descriptions-item label="身体线偏差">
                {{ fmt1(poseAnalysis?.alignment?.body_line_deviation) }}
              </el-descriptions-item>
              <el-descriptions-item label="髋部偏移">{{ fmt1(poseAnalysis?.alignment?.hip_offset) }}</el-descriptions-item>
              <el-descriptions-item label="髋部趋势">{{ hipTrendLabel }}</el-descriptions-item>
            </template>
            <template v-else-if="isPushupAction">
              <el-descriptions-item label="平均肘角">{{ fmt1(poseAnalysis?.angles?.elbow_angle) }}°</el-descriptions-item>
              <el-descriptions-item label="左肘角">{{ fmt1(poseAnalysis?.angles?.left_elbow) }}°</el-descriptions-item>
              <el-descriptions-item label="右肘角">{{ fmt1(poseAnalysis?.angles?.right_elbow) }}°</el-descriptions-item>
              <el-descriptions-item label="肘对称差">{{ fmt1(poseAnalysis?.symmetry?.elbow_diff) }}°</el-descriptions-item>
              <el-descriptions-item label="躯干倾角">{{ fmt1(poseAnalysis?.angles?.torso_lean) }}°</el-descriptions-item>
              <el-descriptions-item label="身体线偏差">
                {{ fmt1(poseAnalysis?.alignment?.body_line_deviation) }}
              </el-descriptions-item>
              <el-descriptions-item label="髋部偏移">{{ fmt1(poseAnalysis?.alignment?.hip_offset) }}</el-descriptions-item>
              <el-descriptions-item label="髋部趋势">{{ hipTrendLabel }}</el-descriptions-item>
              <el-descriptions-item label="动作阶段">{{ pushupPhaseLabel }}</el-descriptions-item>
            </template>
            <template v-else-if="isGluteBridgeAction">
              <el-descriptions-item label="髋伸展角">{{ fmt1(poseAnalysis?.angles?.hip_extension) }}°</el-descriptions-item>
              <el-descriptions-item label="左髋角">{{ fmt1(poseAnalysis?.angles?.left_hip) }}°</el-descriptions-item>
              <el-descriptions-item label="右髋角">{{ fmt1(poseAnalysis?.angles?.right_hip) }}°</el-descriptions-item>
              <el-descriptions-item label="髋对称差">{{ fmt1(poseAnalysis?.symmetry?.hip_diff) }}°</el-descriptions-item>
              <el-descriptions-item label="平均膝角">{{ fmt1(poseAnalysis?.angles?.knee_angle) }}°</el-descriptions-item>
              <el-descriptions-item label="膝对称差">{{ fmt1(poseAnalysis?.symmetry?.knee_diff) }}°</el-descriptions-item>
              <el-descriptions-item label="身体线偏差">
                {{ fmt1(poseAnalysis?.alignment?.body_line_deviation) }}
              </el-descriptions-item>
              <el-descriptions-item label="髋部偏移">{{ fmt1(poseAnalysis?.alignment?.hip_offset) }}</el-descriptions-item>
              <el-descriptions-item label="髋部趋势">{{ hipTrendLabel }}</el-descriptions-item>
              <el-descriptions-item label="动作阶段">{{ gluteBridgePhaseLabel }}</el-descriptions-item>
            </template>
            <template v-else-if="isSitupAction">
              <el-descriptions-item label="髋屈曲角">{{ fmt1(poseAnalysis?.angles?.hip_flexion) }}°</el-descriptions-item>
              <el-descriptions-item label="左髋角">{{ fmt1(poseAnalysis?.angles?.left_hip) }}°</el-descriptions-item>
              <el-descriptions-item label="右髋角">{{ fmt1(poseAnalysis?.angles?.right_hip) }}°</el-descriptions-item>
              <el-descriptions-item label="髋对称差">{{ fmt1(poseAnalysis?.symmetry?.hip_diff) }}°</el-descriptions-item>
              <el-descriptions-item label="平均膝角">{{ fmt1(poseAnalysis?.angles?.knee_angle) }}°</el-descriptions-item>
              <el-descriptions-item label="膝对称差">{{ fmt1(poseAnalysis?.symmetry?.knee_diff) }}°</el-descriptions-item>
              <el-descriptions-item label="躯干角">{{ fmt1(poseAnalysis?.angles?.torso_angle) }}°</el-descriptions-item>
              <el-descriptions-item label="抬起幅度">{{ fmt1(poseAnalysis?.alignment?.torso_raise) }}</el-descriptions-item>
              <el-descriptions-item label="动作阶段">{{ situpPhaseLabel }}</el-descriptions-item>
            </template>
            <template v-else>
              <el-descriptions-item label="左膝角">{{ fmt1(poseAnalysis?.angles?.left_knee) }}°</el-descriptions-item>
              <el-descriptions-item label="右膝角">{{ fmt1(poseAnalysis?.angles?.right_knee) }}°</el-descriptions-item>
              <el-descriptions-item label="左髋角">{{ fmt1(poseAnalysis?.angles?.left_hip) }}°</el-descriptions-item>
              <el-descriptions-item label="右髋角">{{ fmt1(poseAnalysis?.angles?.right_hip) }}°</el-descriptions-item>
              <el-descriptions-item label="躯干前倾角">{{ fmt1(poseAnalysis?.angles?.torso_lean) }}°</el-descriptions-item>
              <el-descriptions-item label="膝对称差">{{ fmt1(poseAnalysis?.symmetry?.knee_diff) }}°</el-descriptions-item>
              <el-descriptions-item label="髋对称差">{{ fmt1(poseAnalysis?.symmetry?.hip_diff) }}°</el-descriptions-item>
            </template>
            <el-descriptions-item label="平均关键点评分">
              {{ fmt3(poseAnalysis?.confidence_summary?.avg_required_score) }}
            </el-descriptions-item>
            <el-descriptions-item label="有效关键点">
              {{ Number(poseAnalysis?.confidence_summary?.valid_required_points || 0) }} /
              {{ Number(poseAnalysis?.confidence_summary?.required_points || 0) }}
            </el-descriptions-item>
            <el-descriptions-item label="有效性说明" :span="2">
              {{ poseAnalysis?.validity?.reason || "关键点充足，可进行评分" }}
            </el-descriptions-item>
          </el-descriptions>
        </el-collapse-item>

        <el-collapse-item
          v-for="(person, index) in personsList"
          :key="index"
          :name="`person-${index}`"
          :title="`人员 ${index + 1} 详情`"
        >
          <el-descriptions :column="2" border>
            <el-descriptions-item label="边界框">
              [{{ person.bbox?.map((v) => Number(v).toFixed(1)).join(", ") }}]
            </el-descriptions-item>
            <el-descriptions-item label="关键点数量">{{ person.keypoints?.length || 0 }}</el-descriptions-item>
            <el-descriptions-item label="有效关键点">{{ getValidCount(person) }}</el-descriptions-item>
            <el-descriptions-item label="平均置信度">{{ getPersonAvgScore(person) }}</el-descriptions-item>
          </el-descriptions>
        </el-collapse-item>
    </el-collapse>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import { ElMessage } from "element-plus";
import { UploadFilled } from "@element-plus/icons-vue";
import { downloadImageResult, inferImage } from "../api/pose";

const file = ref(null);
const loading = ref(false);
const result = ref(null);
const sourceImageUrl = ref("");
const selectedActionType = ref("squat");
const ACTION_LABELS = {
  squat: "深蹲",
  plank: "平板支撑",
  pushup: "俯卧撑",
  glute_bridge: "臀桥",
  situp: "仰卧起坐",
};

const personsList = computed(() => result.value?.persons || []);
const poseAnalysis = computed(() => result.value?.pose_analysis || null);
const poseScoreResult = computed(() => result.value?.pose_score_result || null);
const hasPoseData = computed(() => Boolean(poseAnalysis.value || poseScoreResult.value));
const personsCount = computed(() => personsList.value.length);
const totalKeypoints = computed(() => personsList.value.reduce((sum, p) => sum + (p.keypoints?.length || 0), 0));
const detectedKeypoints = computed(() =>
  personsList.value.reduce((sum, p) => sum + getValidCount(p), 0)
);
const averageConfidence = computed(() => {
  const scores = personsList.value.flatMap((p) =>
    (p.keypoints || []).map((kp) => Number(kp?.[2] || 0)).filter((s) => s > 0)
  );
  if (!scores.length) return "0.000";
  const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
  return avg.toFixed(3);
});
const isMultiPerson = computed(() => personsCount.value > 1);
const modelLabel = computed(() => {
  const full = String(result.value?.model_name || "");
  if (!full) return "未知";
  const normalized = full.replaceAll("\\", "/");
  return normalized.split("/").pop() || full;
});
const actionTypeLabel = computed(() => {
  const action = String(poseAnalysis.value?.action_type || selectedActionType.value || "").toLowerCase();
  if (ACTION_LABELS[action]) return ACTION_LABELS[action];
  return action ? action : "-";
});
const detectionStatusLabel = computed(() => {
  if (loading.value) return "推理中";
  if (result.value) return "已完成";
  if (file.value) return "待推理";
  return "待上传";
});
const isPlankAction = computed(() => String(poseAnalysis.value?.action_type || "").toLowerCase() === "plank");
const isPushupAction = computed(() => String(poseAnalysis.value?.action_type || "").toLowerCase() === "pushup");
const isGluteBridgeAction = computed(() => String(poseAnalysis.value?.action_type || "").toLowerCase() === "glute_bridge");
const isSitupAction = computed(() => String(poseAnalysis.value?.action_type || "").toLowerCase() === "situp");
const hipTrendLabel = computed(() => {
  const t = String(poseAnalysis.value?.alignment?.hip_trend || "");
  if (t === "hip_high") return "髋偏高";
  if (t === "hip_low") return "髋偏低";
  if (t === "normal") return "正常";
  return "-";
});
const pushupPhaseLabel = computed(() => {
  const phase = String(poseAnalysis.value?.alignment?.phase || "");
  if (phase === "top") return "撑起阶段";
  if (phase === "middle") return "过渡阶段";
  if (phase === "bottom") return "下降底部";
  return "-";
});
const gluteBridgePhaseLabel = computed(() => {
  const phase = String(poseAnalysis.value?.alignment?.phase || "");
  if (phase === "top") return "顶峰伸髋";
  if (phase === "middle") return "抬升过渡";
  if (phase === "bottom") return "起始底部";
  return "-";
});
const situpPhaseLabel = computed(() => {
  const phase = String(poseAnalysis.value?.alignment?.phase || "");
  if (phase === "top") return "坐起顶部";
  if (phase === "middle") return "卷腹过渡";
  if (phase === "bottom") return "仰卧底部";
  return "-";
});
const scoringScopeLabel = computed(() => {
  return poseAnalysis.value?.scoring_scope === "main_person_only" ? "主目标单人" : "-";
});
const scoreValue = computed(() => {
  const raw = poseScoreResult.value?.score;
  if (raw === null || raw === undefined || raw === "") return null;
  const n = Number(raw);
  return Number.isFinite(n) ? Math.round(n) : null;
});
const scoreDisplay = computed(() => (scoreValue.value === null ? "-- / 100" : `${scoreValue.value} / 100`));
const scoreComment = computed(() => {
  const c = String(poseScoreResult.value?.overall_comment || "").trim();
  if (c) return c;
  if (poseAnalysis.value && poseAnalysis.value?.validity?.enough_keypoints === false) {
    return "当前图片无法完成可靠动作评分";
  }
  return "暂无评分结果";
});
const problemsList = computed(() => (Array.isArray(poseScoreResult.value?.problems) ? poseScoreResult.value.problems : []));
const suggestionsList = computed(() =>
  Array.isArray(poseScoreResult.value?.suggestions) ? poseScoreResult.value.suggestions : []
);

function onFileChange(uploadFile) {
  file.value = uploadFile.raw;
  if (sourceImageUrl.value) {
    URL.revokeObjectURL(sourceImageUrl.value);
  }
  sourceImageUrl.value = file.value ? URL.createObjectURL(file.value) : "";
}

function onReset() {
  result.value = null;
  file.value = null;
  selectedActionType.value = "squat";
  if (sourceImageUrl.value) {
    URL.revokeObjectURL(sourceImageUrl.value);
  }
  sourceImageUrl.value = "";
}

function getValidCount(person) {
  return (person?.keypoints || []).filter((kp) => Number(kp?.[2] || 0) > 0).length;
}

function getPersonAvgScore(person) {
  const scores = (person?.keypoints || []).map((kp) => Number(kp?.[2] || 0)).filter((s) => s > 0);
  if (!scores.length) return "0.000";
  return (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(3);
}

function fmt1(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(1) : "-";
}

function fmt3(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(3) : "-";
}

async function onInfer() {
  if (!file.value) {
    ElMessage.warning("请先选择图片");
    return;
  }
  loading.value = true;
  try {
    const fd = new FormData();
    fd.append("file", file.value);
    result.value = await inferImage(fd, selectedActionType.value);
    ElMessage.success("推理完成");
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "推理失败");
  } finally {
    loading.value = false;
  }
}

function parseDownloadFilename(contentDisposition, fallback = "pose_result.jpg") {
  if (!contentDisposition) return fallback;
  const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match?.[1]) {
    try {
      return decodeURIComponent(utf8Match[1]);
    } catch {
      return utf8Match[1];
    }
  }
  const plainMatch = contentDisposition.match(/filename="?([^"]+)"?/i);
  return plainMatch?.[1] || fallback;
}

async function onDownloadResult() {
  const detectionId = result.value?.detection_id;
  if (!detectionId) {
    ElMessage.warning("暂无可下载结果");
    return;
  }
  try {
    const resp = await downloadImageResult(detectionId);
    const blobUrl = window.URL.createObjectURL(resp.data);
    const contentDisposition = resp.headers?.["content-disposition"];
    const filename = parseDownloadFilename(contentDisposition, `pose_${detectionId}.jpg`);

    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(blobUrl);
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "下载失败");
  }
}

onBeforeUnmount(() => {
  if (sourceImageUrl.value) {
    URL.revokeObjectURL(sourceImageUrl.value);
  }
});
</script>

<style scoped>
.image-infer-page {
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
  background:
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.overview-trend {
  margin-top: 8px;
  color: #22a6a8;
  font-size: 12px;
}
.operation-grid {
  display: grid;
  grid-template-columns: minmax(420px, 1.05fr) minmax(360px, 0.95fr);
  gap: 18px;
  align-items: stretch;
}
.panel-card,
.image-panel,
.analysis-panel {
  border: 1px solid #e3ecfb;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 42px rgba(64, 97, 150, 0.08);
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
  min-height: 190px;
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
.upload-inner,
.upload-locked {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 130px;
  text-align: center;
}
.upload-locked {
  min-height: 190px;
  border: 1px solid #dfe9fb;
  border-radius: 22px;
  background: #f8fbff;
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
.upload-icon--done {
  background: linear-gradient(135deg, #20c997 0%, #38bdf8 100%);
}
.upload-title {
  color: #1c2e45;
  font-size: 15px;
  font-weight: 800;
}
.upload-desc {
  max-width: 430px;
  color: #7b8da6;
  font-size: 12px;
  line-height: 1.6;
}
.action-selector {
  margin-top: 18px;
}
.action-label {
  margin-bottom: 10px;
  color: #44566e;
  font-size: 13px;
  font-weight: 700;
}
.action-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.action-radio-group :deep(.el-radio-button__inner) {
  border: 1px solid #dfe8f8;
  border-radius: 999px !important;
  color: #4a5f7a;
  background: #fff;
  box-shadow: none;
}
.action-radio-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  border-color: transparent;
  color: #fff;
  background: linear-gradient(135deg, #2f8cff 0%, #7d4dff 100%);
  box-shadow: 0 10px 22px rgba(68, 126, 240, 0.22);
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
  min-width: 118px;
  border-color: #dfe8f8;
  border-radius: 14px;
  color: #37506f;
  background: #fff;
}
.guide-panel {
  display: flex;
  flex-direction: column;
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
  flex: 1;
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
.result-section {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(260px, 1fr) minmax(320px, 0.95fr);
  gap: 18px;
  align-items: stretch;
}
.image-panel,
.analysis-panel {
  overflow: hidden;
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
.image-canvas {
  min-height: 292px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px;
  background: #f7faff;
}
.image-canvas img {
  width: 100%;
  max-height: 430px;
  object-fit: contain;
  border-radius: 16px;
  background: #0f172a;
  box-shadow: 0 14px 30px rgba(24, 44, 78, 0.14);
}
.placeholder {
  min-height: 230px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #8a9bb3;
  text-align: center;
  font-size: 13px;
}
.placeholder-icon {
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
.analysis-panel {
  background: #fff;
}
.analysis-list {
  padding: 16px 18px 8px;
}
.analysis-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 11px 0;
  border-bottom: 1px dashed #e5edf8;
  color: #73859e;
  font-size: 13px;
}
.analysis-row b {
  color: #20324a;
  font-weight: 800;
}
.score-card {
  margin: 12px 18px 18px;
  padding: 14px;
  border: 1px solid #e7effc;
  border-radius: 18px;
  background: linear-gradient(180deg, #fbfdff 0%, #f6f9ff 100%);
}
.score-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #20324a;
  font-weight: 800;
}
.score-main {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.score-block {
  border: 1px solid #e7effc;
  border-radius: 14px;
  background: #fff;
  padding: 10px;
}
.score-label {
  color: #64748b;
  font-size: 12px;
}
.score-value {
  margin-top: 4px;
  color: #1d4ed8;
  font-size: 18px;
  font-weight: 900;
}
.score-comment {
  margin-top: 10px;
  color: #334155;
  line-height: 1.6;
}
.score-list {
  margin-top: 10px;
}
.score-list-title {
  font-size: 13px;
  color: #1e293b;
  font-weight: 600;
}
.score-list ul {
  margin: 6px 0 0;
  padding-left: 18px;
  color: #334155;
}
.score-list li {
  margin: 4px 0;
  line-height: 1.5;
}
.score-empty {
  padding: 22px;
  color: #8a9bb3;
  text-align: center;
  border: 1px dashed #dce8f8;
  border-radius: 14px;
  background: #fff;
}
.detail-collapse {
  border: 1px solid #e3ecfb;
  border-radius: 20px;
  padding: 4px 12px;
  background: #fff;
  box-shadow: 0 14px 34px rgba(64, 97, 150, 0.08);
  overflow: hidden;
}
.detail-collapse :deep(.el-collapse-item__header) {
  color: #20324a;
  font-weight: 800;
}

@media (max-width: 1366px) {
  .hero-card {
    padding: 24px;
  }
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .result-section {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .analysis-panel {
    grid-column: 1 / -1;
  }
}

@media (max-width: 992px) {
  .hero-card,
  .operation-grid,
  .result-section {
    grid-template-columns: 1fr;
  }
  .hero-card {
    flex-direction: column;
  }
  .hero-flow-card {
    width: auto;
    align-self: stretch;
  }
  .score-main {
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
  .operation-grid {
    grid-template-columns: minmax(0, 1fr);
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
