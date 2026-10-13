<template>
  <section class="pose-history-page">
    <div class="hero-card">
      <div class="hero-content">
        <el-tag class="hero-tag" effect="light">Motion Analysis Records</el-tag>
        <h1>动作历史记录</h1>
        <p>集中查看图片姿态推理产生的动作评分、评语与核心指标摘要，支持按动作类型快速筛选。</p>
      </div>
      <div class="hero-summary-card">
        <div class="summary-title">当前筛选</div>
        <div class="summary-action">{{ selectedActionLabel }}</div>
        <div class="summary-note">按检测时间倒序展示最近记录</div>
      </div>
    </div>

    <div class="overview-grid">
      <div class="overview-card">
        <div class="overview-label">历史记录</div>
        <div class="overview-value">{{ total }}</div>
        <div class="overview-trend">当前查询结果</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">平均评分</div>
        <div class="overview-value">{{ averageScoreLabel }}</div>
        <div class="overview-trend">基于当前列表统计</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">动作类型</div>
        <div class="overview-value">{{ selectedActionLabel }}</div>
        <div class="overview-trend">支持五类动作分析</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">数据状态</div>
        <div class="overview-value">{{ loading ? "加载中" : rows.length ? "已就绪" : "暂无数据" }}</div>
        <div class="overview-trend">来自后端动作历史接口</div>
      </div>
    </div>

    <div class="panel-card filter-panel">
      <div class="section-heading">
        <div>
          <h2>筛选条件</h2>
          <p>选择动作类型后刷新列表，可查看对应动作的评分和指标摘要</p>
        </div>
        <el-tag type="info" effect="light">共 {{ total }} 条</el-tag>
      </div>
      <div class="toolbar">
        <el-select v-model="actionType" placeholder="动作类型" class="action-select">
          <el-option label="全部" value="" />
          <el-option label="深蹲" value="squat" />
          <el-option label="平板支撑" value="plank" />
          <el-option label="俯卧撑" value="pushup" />
          <el-option label="臀桥" value="glute_bridge" />
          <el-option label="仰卧起坐" value="situp" />
        </el-select>
        <el-button class="primary-gradient-btn" type="primary" :loading="loading" @click="loadData">查询记录</el-button>
      </div>
    </div>

    <div class="table-panel">
      <div class="panel-title">
        <span>历史明细</span>
        <el-tag effect="light" type="success">按时间倒序</el-tag>
      </div>
      <el-table :data="rows" stripe v-loading="loading" class="history-table" empty-text="暂无动作历史记录">
        <el-table-column prop="created_at" label="检测时间" min-width="180" />
        <el-table-column label="动作类型" width="130">
          <template #default="{ row }">
            <el-tag size="small" :type="actionTagType(row.action_type)" effect="light">
              {{ actionLabel(row.action_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="120">
          <template #default="{ row }">
            <div class="score-pill">{{ scoreLabel(row.score) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="overall_comment" label="评语" min-width="340" show-overflow-tooltip />
        <el-table-column label="核心指标摘要" min-width="360">
          <template #default="{ row }">
            <div class="metrics-brief">{{ metricsBrief(row) }}</div>
          </template>
        </el-table-column>
      </el-table>
      <div class="footer">共 {{ total }} 条记录</div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from "vue";
import { ElMessage } from "element-plus";
import { listPoseHistory } from "../api/pose";

const loading = ref(false);
const actionType = ref("");
const rows = ref([]);
const total = ref(0);
const selectedActionLabel = computed(() => (actionType.value ? actionLabel(actionType.value) : "全部动作"));
const averageScoreLabel = computed(() => {
  const scores = rows.value.map((row) => Number(row.score)).filter((n) => Number.isFinite(n));
  if (!scores.length) return "--";
  const avg = scores.reduce((sum, n) => sum + n, 0) / scores.length;
  return `${Math.round(avg)} / 100`;
});

function actionLabel(action) {
  if (action === "squat") return "深蹲";
  if (action === "plank") return "平板支撑";
  if (action === "pushup") return "俯卧撑";
  if (action === "glute_bridge") return "臀桥";
  if (action === "situp") return "仰卧起坐";
  return action || "-";
}

function actionTagType(action) {
  if (action === "plank") return "success";
  if (action === "pushup") return "primary";
  if (action === "glute_bridge") return "danger";
  if (action === "situp") return "info";
  return "warning";
}

function scoreLabel(score) {
  const n = Number(score);
  return Number.isFinite(n) ? `${Math.round(n)} / 100` : "-- / 100";
}

function metricsBrief(row) {
  const m = row?.metrics_json || {};
  if (row?.action_type === "plank") {
    return `髋角:${m.hip_angle ?? "-"}  躯干:${m.torso_lean ?? "-"}  线偏差:${m.body_line_deviation ?? "-"}  趋势:${m.hip_trend ?? "-"}`;
  }
  if (row?.action_type === "pushup") {
    return `肘角:${m.elbow_angle ?? "-"}  肘差:${m.elbow_diff ?? "-"}  线偏差:${m.body_line_deviation ?? "-"}  阶段:${m.phase ?? "-"}`;
  }
  if (row?.action_type === "glute_bridge") {
    return `髋伸展:${m.hip_extension ?? "-"}  膝角:${m.knee_angle ?? "-"}  线偏差:${m.body_line_deviation ?? "-"}  阶段:${m.phase ?? "-"}`;
  }
  if (row?.action_type === "situp") {
    return `髋屈曲:${m.hip_flexion ?? "-"}  躯干角:${m.torso_angle ?? "-"}  抬起:${m.torso_raise ?? "-"}  阶段:${m.phase ?? "-"}`;
  }
  return `左膝:${m.left_knee ?? "-"}  右膝:${m.right_knee ?? "-"}  膝差:${m.knee_diff ?? "-"}  躯干:${m.torso_lean ?? "-"}`;
}

async function loadData() {
  loading.value = true;
  try {
    const params = { limit: 200 };
    if (actionType.value) params.action_type = actionType.value;
    const data = await listPoseHistory(params);
    rows.value = data?.items || [];
    total.value = Number(data?.total || 0);
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "加载历史记录失败");
  } finally {
    loading.value = false;
  }
}

loadData().catch(() => {});
</script>

<style scoped>
.pose-history-page {
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
  min-height: 156px;
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
.hero-summary-card {
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
}
.hero-content p {
  max-width: 680px;
  margin: 12px 0 0;
  color: #667894;
  font-size: 15px;
  line-height: 1.8;
}
.hero-summary-card {
  align-self: center;
  width: 260px;
  padding: 18px;
  border: 1px solid rgba(220, 230, 247, 0.92);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 16px 36px rgba(70, 107, 160, 0.1);
  backdrop-filter: blur(10px);
}
.summary-title {
  color: #75879f;
  font-size: 12px;
}
.summary-action {
  margin-top: 8px;
  color: #1c2e45;
  font-size: 24px;
  font-weight: 900;
}
.summary-note {
  margin-top: 8px;
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
.panel-card,
.table-panel {
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
  align-items: center;
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
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}
.action-select {
  width: 220px;
}
.primary-gradient-btn {
  min-width: 132px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #2f8cff 0%, #7d4dff 100%);
  box-shadow: 0 14px 28px rgba(77, 132, 255, 0.26);
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
.history-table {
  width: 100%;
}
.history-table :deep(.el-table__header th) {
  color: #50637d;
  background: #f8fbff;
  font-weight: 800;
}
.history-table :deep(.el-table__row) {
  height: 58px;
}
.score-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 74px;
  padding: 5px 10px;
  color: #1d4ed8;
  font-weight: 900;
  border-radius: 999px;
  background: #eef5ff;
}
.metrics-brief {
  color: #475569;
  font-size: 13px;
  line-height: 1.6;
}
.footer {
  padding: 12px 18px 16px;
  color: #64748b;
  font-size: 13px;
  border-top: 1px solid #edf2fb;
  background: #fbfdff;
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
  .hero-card {
    flex-direction: column;
  }
  .hero-summary-card {
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
  .action-select,
  .primary-gradient-btn {
    width: 100%;
  }
}
</style>
