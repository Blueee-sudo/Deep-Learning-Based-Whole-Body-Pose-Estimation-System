<template>
  <section class="pose-trend-page">
    <div class="hero-card">
      <div class="hero-content">
        <el-tag class="hero-tag" effect="light">Motion Trend Analytics</el-tag>
        <h1>动作趋势分析</h1>
        <p>基于历史动作评分和关键指标，追踪训练表现变化，辅助发现动作稳定性与改进趋势。</p>
      </div>
      <div class="hero-summary-card">
        <div class="summary-title">当前分析动作</div>
        <div class="summary-action">{{ selectedActionLabel }}</div>
        <div class="summary-note">评分趋势 + 关键指标趋势</div>
      </div>
    </div>

    <div class="overview-grid">
      <div class="overview-card">
        <div class="overview-label">趋势样本</div>
        <div class="overview-value">{{ rows.length }}</div>
        <div class="overview-trend">最近最多 200 条</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">平均评分</div>
        <div class="overview-value">{{ averageScoreLabel }}</div>
        <div class="overview-trend">基于当前动作历史</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">最新评分</div>
        <div class="overview-value">{{ latestScoreLabel }}</div>
        <div class="overview-trend">最近一次检测结果</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">数据状态</div>
        <div class="overview-value">{{ loading ? "加载中" : hasData ? "已就绪" : "暂无数据" }}</div>
        <div class="overview-trend">来自动作历史接口</div>
      </div>
    </div>

    <div class="panel-card filter-panel">
      <div class="section-heading">
        <div>
          <h2>趋势筛选</h2>
          <p>选择动作类型后刷新图表，查看评分与核心指标的变化走势。</p>
        </div>
        <el-tag type="info" effect="light">{{ selectedActionLabel }}</el-tag>
      </div>
      <div class="toolbar">
        <el-select v-model="actionType" class="action-select">
          <el-option label="深蹲" value="squat" />
          <el-option label="平板支撑" value="plank" />
          <el-option label="俯卧撑" value="pushup" />
          <el-option label="臀桥" value="glute_bridge" />
          <el-option label="仰卧起坐" value="situp" />
        </el-select>
        <el-button class="primary-gradient-btn" type="primary" :loading="loading" @click="loadAndRender">刷新趋势</el-button>
      </div>
    </div>

    <div v-if="!loading && !hasData" class="empty-panel">
      <div class="empty-icon">CHART</div>
      <div class="empty-title">暂无趋势数据</div>
      <div class="empty-desc">请先完成几次 {{ selectedActionLabel }} 图片检测，再回到这里查看趋势。</div>
    </div>

    <div v-show="hasData" class="charts-wrap">
      <div class="chart-panel">
        <div class="panel-title">
          <span>总评分趋势</span>
          <el-tag type="primary" effect="light">0 - 100</el-tag>
        </div>
        <div ref="scoreChartRef" class="chart-box"></div>
      </div>
      <div class="chart-panel">
        <div class="panel-title">
          <span>关键指标趋势</span>
          <el-tag type="success" effect="light">双指标</el-tag>
        </div>
        <div ref="metricChartRef" class="chart-box"></div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import * as echarts from "echarts";
import { listPoseHistory } from "../api/pose";

const actionType = ref("squat");
const loading = ref(false);
const rows = ref([]);
const scoreChartRef = ref(null);
const metricChartRef = ref(null);
let scoreChart = null;
let metricChart = null;

const hasData = computed(() => rows.value.length > 0);
const selectedActionLabel = computed(() => actionLabel(actionType.value));
const averageScoreLabel = computed(() => {
  const scores = rows.value.map((row) => toNumberOrNull(row.score)).filter((n) => n !== null);
  if (!scores.length) return "--";
  const avg = scores.reduce((sum, n) => sum + n, 0) / scores.length;
  return `${Math.round(avg)} / 100`;
});
const latestScoreLabel = computed(() => {
  const n = toNumberOrNull(rows.value?.[0]?.score);
  return n === null ? "--" : `${Math.round(n)} / 100`;
});

function actionLabel(v) {
  if (v === "plank") return "平板支撑";
  if (v === "pushup") return "俯卧撑";
  if (v === "glute_bridge") return "臀桥";
  if (v === "situp") return "仰卧起坐";
  return "深蹲";
}

function toNumberOrNull(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function getMetricValue(item, key) {
  return toNumberOrNull(item?.metrics_json?.[key]);
}

function buildSeriesData() {
  // API returns desc by time; trend charts are easier to read in asc order.
  const ordered = [...rows.value].reverse();
  const x = ordered.map((i) => i.created_at);
  const score = ordered.map((i) => toNumberOrNull(i.score));
  if (actionType.value === "plank") {
    return {
      x,
      score,
      m1: ordered.map((i) => getMetricValue(i, "body_line_deviation")),
      m2: ordered.map((i) => getMetricValue(i, "hip_angle")),
      m1Name: "身体线偏差",
      m2Name: "髋角",
    };
  }
  if (actionType.value === "pushup") {
    return {
      x,
      score,
      m1: ordered.map((i) => getMetricValue(i, "body_line_deviation")),
      m2: ordered.map((i) => getMetricValue(i, "elbow_angle")),
      m1Name: "身体线偏差",
      m2Name: "平均肘角",
    };
  }
  if (actionType.value === "glute_bridge") {
    return {
      x,
      score,
      m1: ordered.map((i) => getMetricValue(i, "body_line_deviation")),
      m2: ordered.map((i) => getMetricValue(i, "hip_extension")),
      m1Name: "身体线偏差",
      m2Name: "髋伸展角",
    };
  }
  if (actionType.value === "situp") {
    return {
      x,
      score,
      m1: ordered.map((i) => getMetricValue(i, "torso_raise")),
      m2: ordered.map((i) => getMetricValue(i, "hip_flexion")),
      m1Name: "抬起幅度",
      m2Name: "髋屈曲角",
    };
  }
  return {
    x,
    score,
    m1: ordered.map((i) => getMetricValue(i, "knee_diff")),
    m2: ordered.map((i) => getMetricValue(i, "torso_lean")),
    m1Name: "膝对称差",
    m2Name: "躯干前倾",
  };
}

function renderCharts() {
  if (!scoreChartRef.value || !metricChartRef.value || !hasData.value) return;
  const data = buildSeriesData();
  if (!scoreChart) scoreChart = echarts.init(scoreChartRef.value);
  if (!metricChart) metricChart = echarts.init(metricChartRef.value);

  scoreChart.setOption({
    title: { text: `${actionLabel(actionType.value)} - 总评分趋势`, left: 8, top: 8, textStyle: { fontSize: 14, color: "#20324a" } },
    color: ["#2f8cff"],
    tooltip: { trigger: "axis" },
    grid: { left: 40, right: 20, top: 50, bottom: 40 },
    xAxis: { type: "category", data: data.x },
    yAxis: { type: "value", min: 0, max: 100 },
    series: [{ name: "score", type: "line", smooth: true, data: data.score, symbolSize: 6 }],
  });

  metricChart.setOption({
    title: { text: `${actionLabel(actionType.value)} - 关键指标趋势`, left: 8, top: 8, textStyle: { fontSize: 14, color: "#20324a" } },
    color: ["#22c7b8", "#7d4dff"],
    tooltip: { trigger: "axis" },
    legend: { top: 8, right: 12, data: [data.m1Name, data.m2Name] },
    grid: { left: 40, right: 20, top: 50, bottom: 40 },
    xAxis: { type: "category", data: data.x },
    yAxis: { type: "value" },
    series: [
      { name: data.m1Name, type: "line", smooth: true, data: data.m1, symbolSize: 6 },
      { name: data.m2Name, type: "line", smooth: true, data: data.m2, symbolSize: 6 },
    ],
  });
}

async function loadAndRender() {
  loading.value = true;
  try {
    const data = await listPoseHistory({ action_type: actionType.value, limit: 200 });
    rows.value = data?.items || [];
    await nextTick();
    if (rows.value.length) {
      renderCharts();
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "加载趋势数据失败");
  } finally {
    loading.value = false;
  }
}

function handleResize() {
  scoreChart?.resize();
  metricChart?.resize();
}

onMounted(() => {
  window.addEventListener("resize", handleResize);
  loadAndRender().catch(() => {});
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  scoreChart?.dispose();
  metricChart?.dispose();
  scoreChart = null;
  metricChart = null;
});
</script>

<style scoped>
.pose-trend-page {
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
.chart-panel,
.empty-panel {
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
.charts-wrap {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
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
.chart-box {
  width: 100%;
  height: 380px;
  background:
    radial-gradient(circle at 100% 0%, rgba(47, 140, 255, 0.08), transparent 32%),
    #fff;
}
.empty-panel {
  min-height: 260px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #8a9bb3;
  text-align: center;
}
.empty-icon {
  display: grid;
  place-items: center;
  width: 64px;
  height: 64px;
  color: #6d8ee8;
  font-size: 12px;
  font-weight: 900;
  border-radius: 22px;
  background: #eef5ff;
}
.empty-title {
  color: #20324a;
  font-size: 17px;
  font-weight: 900;
}
.empty-desc {
  color: #7a8ba4;
  font-size: 13px;
}

@media (max-width: 1366px) {
  .hero-card {
    padding: 24px;
  }
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .charts-wrap {
    grid-template-columns: 1fr;
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
  .chart-box {
    height: 320px;
  }
}
</style>
