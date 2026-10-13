<template>
  <section class="admin-page">
    <div class="hero-card">
      <div class="hero-content">
        <el-tag class="hero-tag" effect="light">Admin Console</el-tag>
        <h1>管理员面板</h1>
        <p>统一查看用户、检测任务、操作日志和模型指标，辅助管理全身姿态关键点定位系统运行状态。</p>
      </div>
      <div class="hero-summary-card">
        <div class="summary-title">当前模块</div>
        <div class="summary-action">{{ tabLabel }}</div>
        <div class="summary-note">管理员专属数据视图</div>
      </div>
    </div>

    <div class="overview-grid">
      <div class="overview-card">
        <div class="overview-label">用户数量</div>
        <div class="overview-value">{{ users.length }}</div>
        <div class="overview-trend">最近 20 条用户</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">检测记录</div>
        <div class="overview-value">{{ detections.length }}</div>
        <div class="overview-trend">最近 20 条任务</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">操作日志</div>
        <div class="overview-value">{{ logs.length }}</div>
        <div class="overview-trend">最近 20 条日志</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">模型指标</div>
        <div class="overview-value">{{ metrics.length }}</div>
        <div class="overview-trend">{{ metricFilterSummary }}</div>
      </div>
    </div>

    <div class="console-panel">
      <div class="panel-title">
        <span>系统管理控制台</span>
        <el-tag effect="light" type="success">管理端</el-tag>
      </div>
      <el-tabs v-model="tab" class="admin-tabs">
        <el-tab-pane label="用户" name="users">
          <div class="user-manage-toolbar">
            <div>
              <div class="toolbar-title">普通用户管理</div>
              <div class="toolbar-desc">管理员可新增、查看、编辑、删除普通用户账号。</div>
            </div>
            <el-button class="primary-gradient-btn" type="primary" @click="openCreateUser">新增普通用户</el-button>
          </div>
          <el-table :data="users" stripe class="admin-table" empty-text="暂无用户数据">
            <el-table-column prop="user_id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" min-width="160" />
            <el-table-column prop="email" label="邮箱" min-width="220" />
            <el-table-column label="角色" width="120">
              <template #default="{ row }">
                <el-tag :type="row.role_id === 1 ? 'primary' : 'info'" effect="light">
                  {{ roleLabel(row.role_id) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'" effect="light">
                  {{ row.is_active ? "启用" : "禁用" }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" min-width="180" />
            <el-table-column label="操作" width="230" fixed="right">
              <template #default="{ row }">
                <el-button size="small" class="mini-btn" @click="openViewUser(row)">查看</el-button>
                <el-button size="small" class="mini-btn" @click="openEditUser(row)">编辑</el-button>
                <el-button size="small" type="danger" plain @click="removeUser(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="检测记录" name="detections">
          <el-table :data="detections" stripe class="admin-table" empty-text="暂无检测记录">
            <el-table-column prop="detection_id" label="ID" width="80" />
            <el-table-column prop="user" label="用户ID" width="100" />
            <el-table-column label="类型" width="120">
              <template #default="{ row }">
                <el-tag :type="inputTypeTag(row.input_type)" effect="light">{{ inputTypeLabel(row.input_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="statusTag(row.status)" effect="light">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" min-width="180" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="日志" name="logs">
          <el-table :data="logs" stripe class="admin-table" empty-text="暂无操作日志">
            <el-table-column prop="log_id" label="ID" width="80" />
            <el-table-column prop="action" label="行为" width="140" />
            <el-table-column prop="user" label="用户" width="90" />
            <el-table-column prop="request_path" label="路径" min-width="260" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" min-width="180" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="指标" name="metrics">
          <div class="metric-filter-card">
            <div class="section-heading">
              <div>
                <h2>指标筛选</h2>
                <p>筛选模型名称、指标类型和关键点子集后刷新指标图。</p>
              </div>
              <el-tag type="info" effect="light">{{ metricFilterSummary }}</el-tag>
            </div>
            <el-form inline class="metric-form">
              <el-form-item label="模型">
                <el-input v-model="metricFilter.model_name" placeholder="可选" clearable />
              </el-form-item>
              <el-form-item label="指标">
                <el-input v-model="metricFilter.metric_type" placeholder="如 AP" clearable />
              </el-form-item>
              <el-form-item label="子集">
                <el-input v-model="metricFilter.keypoint_subset" placeholder="wholebody/body/face" clearable />
              </el-form-item>
              <el-form-item>
                <el-button class="primary-gradient-btn" type="primary" @click="loadMetricPlot">刷新图表</el-button>
              </el-form-item>
            </el-form>
          </div>

          <div class="metrics-grid">
            <div class="plot-panel">
              <div class="sub-panel-title">指标图表</div>
              <div v-if="plotUrl" class="plot-wrap">
                <img :src="plotUrl" alt="metrics plot" />
              </div>
              <div v-else class="empty-plot">
                <div class="empty-icon">PLOT</div>
                <div>暂无指标图，请刷新或导入指标数据</div>
              </div>
            </div>

            <div class="metric-table-panel">
              <div class="sub-panel-title">指标明细</div>
              <el-table :data="metrics" stripe class="admin-table" empty-text="暂无指标数据">
                <el-table-column prop="metric_id" label="ID" width="80" />
                <el-table-column prop="model_name" label="模型" min-width="180" show-overflow-tooltip />
                <el-table-column prop="metric_type" label="指标" width="100" />
                <el-table-column prop="metric_value" label="值" width="90" />
                <el-table-column prop="evaluated_at" label="日期" min-width="160" />
              </el-table>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog v-model="userDialogVisible" :title="userDialogTitle" width="560px" class="user-dialog" destroy-on-close>
      <el-form :model="userForm" label-width="92px" class="user-form">
        <el-form-item label="用户ID" v-if="userDialogMode !== 'create'">
          <el-input v-model="userForm.user_id" disabled />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" :disabled="userDialogMode === 'view'" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" :disabled="userDialogMode === 'view'" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="userForm.password"
            :disabled="userDialogMode === 'view'"
            type="password"
            show-password
            :placeholder="userDialogMode === 'create' ? '至少 8 位密码' : '留空则不修改密码'"
          />
        </el-form-item>
        <el-form-item label="头像地址">
          <el-input v-model="userForm.avatar_url" :disabled="userDialogMode === 'view'" placeholder="可选" />
        </el-form-item>
        <el-form-item label="账号状态">
          <el-switch
            v-model="userForm.is_active"
            :disabled="userDialogMode === 'view'"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">{{ userDialogMode === "view" ? "关闭" : "取消" }}</el-button>
        <el-button
          v-if="userDialogMode !== 'view'"
          class="primary-gradient-btn"
          type="primary"
          :loading="savingUser"
          @click="submitUser"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  adminDetections,
  adminLogs,
  adminMetrics,
  adminMetricsPlot,
  adminUsers,
  createAdminUser,
  deleteAdminUser,
  getAdminUser,
  updateAdminUser,
} from "../api/admin";

const tab = ref("users");
const users = ref([]);
const detections = ref([]);
const logs = ref([]);
const metrics = ref([]);
const plotUrl = ref("");
const metricFilter = ref({
  model_name: "",
  metric_type: "",
  keypoint_subset: "",
});
const userDialogVisible = ref(false);
const userDialogMode = ref("create");
const savingUser = ref(false);
const userForm = reactive({
  user_id: "",
  username: "",
  email: "",
  password: "",
  avatar_url: "",
  is_active: true,
});
const tabLabel = computed(() => {
  if (tab.value === "detections") return "检测记录";
  if (tab.value === "logs") return "操作日志";
  if (tab.value === "metrics") return "模型指标";
  return "用户管理";
});
const metricFilterSummary = computed(() => {
  const values = Object.values(metricFilter.value).filter((value) => String(value || "").trim() !== "");
  return values.length ? `${values.length} 个筛选条件` : "全部指标";
});
const userDialogTitle = computed(() => {
  if (userDialogMode.value === "view") return "查看普通用户";
  if (userDialogMode.value === "edit") return "编辑普通用户";
  return "新增普通用户";
});

function normalizedMetricFilter() {
  return Object.fromEntries(
    Object.entries(metricFilter.value).filter(([, value]) => String(value || "").trim() !== ""),
  );
}

function clearPlotUrl() {
  if (plotUrl.value) {
    URL.revokeObjectURL(plotUrl.value);
    plotUrl.value = "";
  }
}

async function loadMetricPlot() {
  clearPlotUrl();
  try {
    const blob = await adminMetricsPlot(normalizedMetricFilter());
    plotUrl.value = URL.createObjectURL(blob);
  } catch {
    // ignore when there are no metrics yet
  }
}

async function loadAll() {
  const metricParams = normalizedMetricFilter();
  const [u, d, l, m] = await Promise.all([
    adminUsers({ page: 1, size: 20, role_id: 2 }),
    adminDetections({ page: 1, size: 20 }),
    adminLogs({ page: 1, size: 20 }),
    adminMetrics(metricParams),
  ]);
  users.value = u.items || [];
  detections.value = d.items || [];
  logs.value = l.items || [];
  metrics.value = m || [];
  loadMetricPlot();
}

loadAll().catch(() => {});
onBeforeUnmount(() => clearPlotUrl());

function resetUserForm() {
  Object.assign(userForm, {
    user_id: "",
    username: "",
    email: "",
    password: "",
    avatar_url: "",
    is_active: true,
  });
}

function fillUserForm(user) {
  Object.assign(userForm, {
    user_id: user.user_id || "",
    username: user.username || "",
    email: user.email || "",
    password: "",
    avatar_url: user.avatar_url || "",
    is_active: Boolean(user.is_active),
  });
}

function openCreateUser() {
  resetUserForm();
  userDialogMode.value = "create";
  userDialogVisible.value = true;
}

async function openViewUser(row) {
  const user = await getAdminUser(row.user_id);
  fillUserForm(user);
  userDialogMode.value = "view";
  userDialogVisible.value = true;
}

async function openEditUser(row) {
  const user = await getAdminUser(row.user_id);
  fillUserForm(user);
  userDialogMode.value = "edit";
  userDialogVisible.value = true;
}

function buildUserPayload() {
  const payload = {
    username: userForm.username,
    email: userForm.email,
    avatar_url: userForm.avatar_url,
    is_active: userForm.is_active,
  };
  if (userDialogMode.value === "create" || userForm.password) {
    payload.password = userForm.password;
  }
  return payload;
}

async function submitUser() {
  savingUser.value = true;
  try {
    if (userDialogMode.value === "create") {
      await createAdminUser(buildUserPayload());
      ElMessage.success("普通用户创建成功");
    } else {
      await updateAdminUser(userForm.user_id, buildUserPayload());
      ElMessage.success("普通用户更新成功");
    }
    userDialogVisible.value = false;
    await loadAll();
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "保存用户失败");
  } finally {
    savingUser.value = false;
  }
}

async function removeUser(row) {
  try {
    await ElMessageBox.confirm(`确认删除普通用户「${row.username}」吗？该操作不可恢复。`, "删除用户", {
      confirmButtonText: "确认删除",
      cancelButtonText: "取消",
      type: "warning",
    });
    await deleteAdminUser(row.user_id);
    ElMessage.success("删除成功");
    await loadAll();
  } catch (e) {
    if (e !== "cancel" && e !== "close") {
      ElMessage.error(e?.response?.data?.detail || "删除用户失败");
    }
  }
}

function roleLabel(roleId) {
  return Number(roleId) === 1 ? "管理员" : "普通用户";
}

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
</script>

<style scoped>
.admin-page {
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
.console-panel,
.metric-filter-card,
.plot-panel,
.metric-table-panel {
  border: 1px solid #e3ecfb;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 42px rgba(64, 97, 150, 0.08);
  overflow: hidden;
}
.panel-title,
.sub-panel-title {
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
.admin-tabs {
  padding: 0 18px 18px;
}
.admin-tabs :deep(.el-tabs__header) {
  margin: 0 0 16px;
}
.admin-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: #edf2fb;
}
.admin-tabs :deep(.el-tabs__item) {
  height: 48px;
  color: #61738c;
  font-weight: 700;
}
.admin-tabs :deep(.el-tabs__item.is-active) {
  color: #2f6ce5;
}
.admin-table {
  width: 100%;
}
.admin-table :deep(.el-table__header th) {
  color: #50637d;
  background: #f8fbff;
  font-weight: 800;
}
.admin-table :deep(.el-table__row) {
  height: 56px;
}
.user-manage-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #e3ecfb;
  border-radius: 18px;
  background: linear-gradient(135deg, #f8fbff 0%, #f3f7ff 100%);
}
.toolbar-title {
  color: #1c2e45;
  font-size: 16px;
  font-weight: 900;
}
.toolbar-desc {
  margin-top: 6px;
  color: #73859e;
  font-size: 13px;
}
.mini-btn {
  border-color: #d9e6fb;
  color: #2f6ce5;
  background: #f6faff;
}
.metric-filter-card {
  padding: 18px;
  margin-bottom: 18px;
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
.metric-form {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
}
.primary-gradient-btn {
  min-width: 132px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #2f8cff 0%, #7d4dff 100%);
  box-shadow: 0 14px 28px rgba(77, 132, 255, 0.26);
}
.metrics-grid {
  display: grid;
  grid-template-columns: minmax(360px, 0.9fr) minmax(420px, 1.1fr);
  gap: 18px;
}
.plot-wrap {
  padding: 18px;
  background: #f8fbff;
}
.plot-wrap img {
  display: block;
  max-width: 100%;
  border: 1px solid #e3ecfb;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 14px 30px rgba(64, 97, 150, 0.08);
}
.empty-plot {
  min-height: 260px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #8a9bb3;
  text-align: center;
  background: #f8fbff;
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
.user-form {
  padding: 6px 6px 0;
}
.user-dialog :deep(.el-dialog) {
  border-radius: 22px;
  overflow: hidden;
}
.user-dialog :deep(.el-dialog__header) {
  padding: 18px 22px;
  margin: 0;
  border-bottom: 1px solid #edf2fb;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}
.user-dialog :deep(.el-dialog__title) {
  color: #20324a;
  font-weight: 900;
}
.user-dialog :deep(.el-dialog__footer) {
  padding: 14px 22px 18px;
  border-top: 1px solid #edf2fb;
}

@media (max-width: 1366px) {
  .hero-card {
    padding: 24px;
  }
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .metrics-grid {
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
  .user-manage-toolbar {
    align-items: stretch;
    flex-direction: column;
  }
  .hero-content h1 {
    font-size: 26px;
  }
}
</style>
