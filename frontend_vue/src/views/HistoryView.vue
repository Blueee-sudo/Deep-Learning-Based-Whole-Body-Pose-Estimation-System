<template>
  <section class="history-page">
    <div class="hero-card">
      <div class="hero-content">
        <el-tag class="hero-tag" effect="light">Detection Records</el-tag>
        <h1>检测历史</h1>
        <p>统一管理图片、视频与实时检测产生的历史记录，支持按输入类型、任务状态筛选，并导出数据报表。</p>
      </div>
      <div class="hero-summary-card">
        <div class="summary-title">当前筛选</div>
        <div class="summary-action">{{ filterSummary }}</div>
        <div class="summary-note">分页展示检测任务记录</div>
      </div>
    </div>

    <div class="overview-grid">
      <div class="overview-card">
        <div class="overview-label">历史记录</div>
        <div class="overview-value">{{ total }}</div>
        <div class="overview-trend">当前查询总数</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">当前页记录</div>
        <div class="overview-value">{{ rows.length }}</div>
        <div class="overview-trend">每页 {{ query.size }} 条</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">平均耗时</div>
        <div class="overview-value">{{ averageInferMs }}</div>
        <div class="overview-trend">基于当前页统计</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">数据状态</div>
        <div class="overview-value">{{ loading ? "加载中" : rows.length ? "已就绪" : "暂无数据" }}</div>
        <div class="overview-trend">来自检测历史接口</div>
      </div>
    </div>

    <div class="panel-card filter-panel">
      <div class="section-heading">
        <div>
          <h2>筛选与导出</h2>
          <p>按检测来源和任务状态筛选记录，也可以导出 CSV 或 Excel 报表。</p>
        </div>
        <el-tag type="info" effect="light">第 {{ query.page }} 页</el-tag>
      </div>
      <div class="toolbar">
        <el-select v-model="filters.input_type" placeholder="类型" clearable class="filter-select">
          <el-option label="图片" value="image" />
          <el-option label="视频" value="video" />
          <el-option label="实时" value="realtime" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable class="filter-select">
          <el-option label="完成" value="done" />
          <el-option label="处理中" value="processing" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-button class="primary-gradient-btn" :loading="loading" type="primary" @click="loadData">查询记录</el-button>
        <el-button class="ghost-btn" :loading="exporting === 'csv'" @click="exportData('csv')">导出 CSV</el-button>
        <el-button class="ghost-btn" :loading="exporting === 'excel'" @click="exportData('excel')">导出 Excel</el-button>
      </div>
    </div>

    <div class="table-panel">
      <div class="panel-title">
        <span>检测明细</span>
        <el-tag effect="light" type="success">支持详情 / 删除</el-tag>
      </div>
      <el-table :data="rows" stripe v-loading="loading" class="history-table" empty-text="暂无检测历史记录">
        <el-table-column prop="detection_id" label="ID" width="90" />
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            <el-tag size="small" :type="inputTypeTag(row.input_type)" effect="light">
              {{ inputTypeLabel(row.input_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="statusTag(row.status)" effect="light">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="person_count" label="人数" width="80" />
        <el-table-column prop="frame_count" label="帧数" width="80" />
        <el-table-column label="耗时(ms)" width="120">
          <template #default="{ row }">
            <span class="time-pill">{{ Math.round(Number(row.inference_time_ms || 0)) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" min-width="180" />
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="{ row }">
            <el-button size="small" class="mini-btn" @click="showDetail(row)">详情</el-button>
            <el-button size="small" type="danger" plain @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
      <el-pagination
        layout="total, prev, pager, next"
        :total="total"
        :page-size="query.size"
        :current-page="query.page"
        @current-change="changePage"
      />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { deleteHistory, exportHistoryFile, getHistoryDetail, listHistory } from "../api/history";

const query = reactive({ page: 1, size: 20 });
const filters = reactive({ input_type: "", status: "" });
const rows = ref([]);
const total = ref(0);
const loading = ref(false);
const exporting = ref("");
const filterSummary = computed(() => {
  const parts = [];
  if (filters.input_type) parts.push(inputTypeLabel(filters.input_type));
  if (filters.status) parts.push(statusLabel(filters.status));
  return parts.length ? parts.join(" / ") : "全部记录";
});
const averageInferMs = computed(() => {
  const values = rows.value.map((row) => Number(row.inference_time_ms)).filter((n) => Number.isFinite(n) && n > 0);
  if (!values.length) return "--";
  const avg = values.reduce((sum, n) => sum + n, 0) / values.length;
  return `${Math.round(avg)} ms`;
});

function inputTypeLabel(type) {
  if (type === "image") return "图片";
  if (type === "video") return "视频";
  if (type === "realtime") return "实时";
  return type || "-";
}

function inputTypeTag(type) {
  if (type === "image") return "primary";
  if (type === "video") return "success";
  if (type === "realtime") return "warning";
  return "info";
}

function statusLabel(status) {
  if (status === "done") return "完成";
  if (status === "processing") return "处理中";
  if (status === "failed") return "失败";
  return status || "-";
}

function statusTag(status) {
  if (status === "done") return "success";
  if (status === "processing") return "warning";
  if (status === "failed") return "danger";
  return "info";
}

async function loadData() {
  loading.value = true;
  try {
    const data = await listHistory({ ...query, ...filters });
    rows.value = data.items || [];
    total.value = data.total || 0;
  } finally {
    loading.value = false;
  }
}

async function showDetail(row) {
  const data = await getHistoryDetail(row.detection_id, { with_keypoints: true, frame_index: 0 });
  ElMessage.info(`记录 ${row.detection_id}，关键点条目: ${(data.keypoints || []).length}`);
}

function getDownloadFilename(headers, fmt) {
  const disposition = headers?.["content-disposition"] || "";
  const match = disposition.match(/filename="?([^"]+)"?/i);
  if (match?.[1]) return decodeURIComponent(match[1]);
  return fmt === "excel" ? "history.xlsx" : "history.csv";
}

async function exportData(fmt) {
  exporting.value = fmt;
  try {
    const { data, headers } = await exportHistoryFile(fmt, filters);
    const blob = new Blob([data], {
      type:
        fmt === "excel"
          ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          : "text/csv;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = getDownloadFilename(headers, fmt);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    ElMessage.success(fmt === "excel" ? "Excel 导出成功" : "CSV 导出成功");
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "导出失败，请确认登录状态和后端服务");
  } finally {
    exporting.value = "";
  }
}

async function remove(row) {
  await deleteHistory(row.detection_id);
  ElMessage.success("删除成功");
  await loadData();
}

async function changePage(p) {
  query.page = p;
  await loadData();
}

loadData().catch(() => {});
</script>

<style scoped>
.history-page {
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
.filter-select {
  width: 180px;
}
.primary-gradient-btn {
  min-width: 132px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #2f8cff 0%, #7d4dff 100%);
  box-shadow: 0 14px 28px rgba(77, 132, 255, 0.26);
}
.ghost-btn {
  border-color: #dfe8f8;
  border-radius: 14px;
  color: #37506f;
  background: #fff;
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
.time-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 62px;
  padding: 5px 10px;
  color: #1d4ed8;
  font-weight: 900;
  border-radius: 999px;
  background: #eef5ff;
}
.mini-btn {
  border-color: #dfe8f8;
  color: #37506f;
  background: #fff;
}
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 14px 18px 16px;
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
  .filter-select,
  .primary-gradient-btn,
  .toolbar a,
  .ghost-btn {
    width: 100%;
  }
  .pagination-wrap {
    justify-content: center;
  }
}
</style>
