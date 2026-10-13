<template>
  <section class="home-page">
    <div class="hero-card">
      <div class="hero-content">
        <el-tag class="hero-tag" effect="light">Whole-Body Pose Intelligence</el-tag>
        <h1>基于深度学习的全身姿态关键点定位系统</h1>
        <p>
          面向图片、视频与实时摄像头场景，系统集成人体全身关键点检测、动作姿态分析、历史记录管理与趋势可视化，
          为运动训练、动作评估和姿态研究提供一站式智能分析平台。
        </p>
        <div class="hero-actions">
          <el-button class="primary-gradient-btn" type="primary" @click="go('/image')">开始图片检测</el-button>
          <el-button class="ghost-btn" @click="go('/video')">视频姿态检测</el-button>
          <el-button class="ghost-btn" @click="go('/realtime')">实时检测体验</el-button>
        </div>
      </div>
      <div class="hero-visual">
        <div class="visual-orbit"></div>
        <div class="skeleton-card">
          <div class="skeleton-head"></div>
          <div class="skeleton-body">
            <span class="joint joint-a"></span>
            <span class="joint joint-b"></span>
            <span class="joint joint-c"></span>
            <span class="joint joint-d"></span>
            <span class="joint joint-e"></span>
          </div>
          <div class="visual-title">133 Keypoints</div>
          <div class="visual-subtitle">Body / Face / Hands</div>
        </div>
      </div>
    </div>

    <div class="overview-grid">
      <div class="overview-card">
        <div class="overview-label">检测模式</div>
        <div class="overview-value">3 类</div>
        <div class="overview-trend">图片 / 视频 / 实时</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">支持动作</div>
        <div class="overview-value">5 项</div>
        <div class="overview-trend">深蹲、平板、俯卧撑等</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">关键点能力</div>
        <div class="overview-value">133</div>
        <div class="overview-trend">全身姿态定位</div>
      </div>
      <div class="overview-card">
        <div class="overview-label">数据闭环</div>
        <div class="overview-value">完整</div>
        <div class="overview-trend">历史 / 动作 / 趋势</div>
      </div>
    </div>

    <div class="section-grid">
      <div class="panel-card feature-panel">
        <div class="section-heading">
          <div>
            <h2>核心功能</h2>
            <p>系统围绕姿态检测、动作分析和数据管理构建完整工作流。</p>
          </div>
          <el-tag type="success" effect="light">AI Dashboard</el-tag>
        </div>
        <div class="feature-grid">
          <div v-for="item in features" :key="item.title" class="feature-item">
            <div class="feature-icon">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="panel-card workflow-panel">
        <div class="section-heading">
          <div>
            <h2>检测流程</h2>
            <p>从数据输入到可视化结果生成，形成清晰的端到端分析链路。</p>
          </div>
        </div>
        <div class="timeline">
          <div v-for="(step, index) in workflow" :key="step.title" class="timeline-item">
            <div class="timeline-index">{{ index + 1 }}</div>
            <div>
              <h3>{{ step.title }}</h3>
              <p>{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="action-section">
      <div class="section-heading">
        <div>
          <h2>动作分析能力</h2>
          <p>支持多类常见训练动作的姿态评分、问题定位与改进建议。</p>
        </div>
        <el-tag type="primary" effect="light">Pose Scoring</el-tag>
      </div>
      <div class="action-grid">
        <div v-for="action in actions" :key="action.name" class="action-card">
          <div class="action-name">{{ action.name }}</div>
          <div class="action-en">{{ action.en }}</div>
          <p>{{ action.desc }}</p>
        </div>
      </div>
    </div>

    <div class="bottom-grid">
      <div class="panel-card tech-panel">
        <div class="section-heading">
          <div>
            <h2>技术架构</h2>
            <p>Django 后端、Vue 前端与深度学习推理服务协同工作。</p>
          </div>
        </div>
        <div class="tech-list">
          <span>Django</span>
          <span>Vue 3</span>
          <span>Element Plus</span>
          <span>MMPose</span>
          <span>OpenCV</span>
          <span>ECharts</span>
        </div>
      </div>

      <div class="panel-card quick-panel">
        <div class="section-heading">
          <div>
            <h2>快捷入口</h2>
            <p>快速进入检测、记录和分析页面。</p>
          </div>
        </div>
        <div class="quick-links">
          <button v-for="link in quickLinks" :key="link.path" type="button" @click="go(link.path)">
            <span>{{ link.title }}</span>
            <small>{{ link.desc }}</small>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from "vue-router";
import {
  Camera,
  Clock,
  DataAnalysis,
  Picture,
  TrendCharts,
  VideoCamera,
} from "@element-plus/icons-vue";

const router = useRouter();

const features = [
  { title: "图片姿态推理", desc: "上传单张人体动作图片，自动生成关键点可视化结果和动作分析。", icon: Picture },
  { title: "视频姿态检测", desc: "支持视频文件逐帧分析，输出处理进度和检测结果视频。", icon: VideoCamera },
  { title: "实时摄像头检测", desc: "调用本地摄像头进行实时关键点定位，支持 WebSocket 与 HTTP 推理链路。", icon: Camera },
  { title: "历史数据管理", desc: "集中管理检测任务、动作评分和模型推理记录，便于回溯分析。", icon: Clock },
  { title: "趋势分析", desc: "基于历史动作评分绘制趋势图，观察训练表现和姿态变化。", icon: TrendCharts },
  { title: "管理控制台", desc: "管理员可查看系统用户、检测记录、操作日志和模型指标。", icon: DataAnalysis },
];

const workflow = [
  { title: "输入检测数据", desc: "选择图片、视频或实时摄像头作为姿态分析来源。" },
  { title: "模型关键点定位", desc: "调用深度学习模型识别人体全身关键点，覆盖身体、面部和手部。" },
  { title: "动作姿态分析", desc: "根据关键点几何关系计算角度、对齐度、稳定性和动作阶段。" },
  { title: "结果沉淀展示", desc: "生成可视化结果、动作评分、历史记录与趋势图表。" },
];

const actions = [
  { name: "深蹲", en: "Squat", desc: "关注膝关节、髋关节角度与身体稳定性。" },
  { name: "平板支撑", en: "Plank", desc: "分析肩、髋、踝对齐程度和核心稳定表现。" },
  { name: "俯卧撑", en: "Push-up", desc: "评估肘部角度、躯干控制和左右对称性。" },
  { name: "臀桥", en: "Glute Bridge", desc: "关注髋部伸展、膝髋对齐和骨盆控制。" },
  { name: "仰卧起坐", en: "Sit-up", desc: "分析躯干屈曲幅度、髋膝角度和动作阶段。" },
];

const quickLinks = [
  { title: "图片检测", desc: "上传图片并获取姿态结果", path: "/image" },
  { title: "视频检测", desc: "处理视频动作关键点", path: "/video" },
  { title: "实时检测", desc: "打开摄像头实时分析", path: "/realtime" },
  { title: "动作历史", desc: "查看动作评分记录", path: "/pose-history" },
  { title: "趋势分析", desc: "查看评分变化趋势", path: "/pose-trends" },
];

function go(path) {
  router.push(path);
}
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
  color: #102033;
}
.hero-card {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.65fr);
  gap: 28px;
  min-height: 300px;
  padding: 32px;
  overflow: hidden;
  border: 1px solid rgba(214, 226, 248, 0.9);
  border-radius: 30px;
  background:
    radial-gradient(circle at 82% 18%, rgba(47, 140, 255, 0.22), transparent 28%),
    radial-gradient(circle at 20% 90%, rgba(125, 77, 255, 0.13), transparent 30%),
    linear-gradient(135deg, #f7fbff 0%, #edf5ff 50%, #f8f5ff 100%);
  box-shadow: 0 24px 56px rgba(60, 93, 148, 0.12);
}
.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.hero-tag {
  width: fit-content;
  margin-bottom: 16px;
  border-color: rgba(82, 132, 255, 0.18);
  color: #2f6ce5;
  background: rgba(255, 255, 255, 0.75);
}
.hero-content h1 {
  max-width: 780px;
  margin: 0;
  color: #102033;
  font-size: 38px;
  line-height: 1.18;
  letter-spacing: -0.5px;
}
.hero-content p {
  max-width: 780px;
  margin: 16px 0 0;
  color: #667894;
  font-size: 15px;
  line-height: 1.9;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}
.primary-gradient-btn {
  min-width: 132px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #2f8cff 0%, #7d4dff 100%);
  box-shadow: 0 14px 28px rgba(77, 132, 255, 0.26);
}
.ghost-btn {
  min-width: 120px;
  border-color: #dbe7fb;
  border-radius: 14px;
  color: #2f6ce5;
  background: rgba(255, 255, 255, 0.72);
}
.hero-visual {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 240px;
}
.visual-orbit {
  position: absolute;
  width: 260px;
  height: 260px;
  border: 1px dashed rgba(89, 126, 220, 0.32);
  border-radius: 999px;
}
.skeleton-card {
  position: relative;
  z-index: 1;
  width: 250px;
  padding: 24px;
  border: 1px solid rgba(220, 230, 247, 0.92);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 18px 42px rgba(70, 107, 160, 0.12);
  text-align: center;
  backdrop-filter: blur(10px);
}
.skeleton-head {
  width: 44px;
  height: 44px;
  margin: 0 auto 14px;
  border-radius: 999px;
  background: linear-gradient(135deg, #2f8cff, #7d4dff);
}
.skeleton-body {
  position: relative;
  height: 118px;
  margin: 0 auto 18px;
}
.skeleton-body::before,
.skeleton-body::after {
  content: "";
  position: absolute;
  left: 50%;
  width: 2px;
  height: 110px;
  background: linear-gradient(180deg, #4d84ff, rgba(77, 132, 255, 0.08));
  transform: translateX(-50%);
}
.skeleton-body::after {
  top: 38px;
  width: 150px;
  height: 2px;
  background: linear-gradient(90deg, rgba(77, 132, 255, 0.08), #4d84ff, rgba(77, 132, 255, 0.08));
}
.joint {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: #22a6a8;
  box-shadow: 0 0 0 8px rgba(34, 166, 168, 0.12);
}
.joint-a {
  left: 50%;
  top: 10px;
  transform: translateX(-50%);
}
.joint-b {
  left: 28px;
  top: 34px;
}
.joint-c {
  right: 28px;
  top: 34px;
}
.joint-d {
  left: 58px;
  bottom: 8px;
}
.joint-e {
  right: 58px;
  bottom: 8px;
}
.visual-title {
  color: #1c2e45;
  font-size: 24px;
  font-weight: 900;
}
.visual-subtitle {
  margin-top: 6px;
  color: #73859e;
  font-size: 13px;
}
.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}
.overview-card,
.panel-card,
.action-section {
  border: 1px solid #e3ecfb;
  border-radius: 24px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: 0 16px 38px rgba(64, 97, 150, 0.08);
}
.overview-card {
  min-height: 110px;
  padding: 18px;
}
.overview-label {
  color: #75879f;
  font-size: 12px;
}
.overview-value {
  margin-top: 10px;
  color: #12233a;
  font-size: 24px;
  font-weight: 900;
}
.overview-trend {
  margin-top: 8px;
  color: #22a6a8;
  font-size: 12px;
}
.section-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(360px, 0.65fr);
  gap: 18px;
}
.panel-card,
.action-section {
  padding: 22px;
}
.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}
.section-heading h2 {
  margin: 0;
  color: #1c2e45;
  font-size: 20px;
}
.section-heading p {
  margin: 8px 0 0;
  color: #73859e;
  font-size: 13px;
  line-height: 1.7;
}
.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.feature-item {
  display: flex;
  gap: 14px;
  min-height: 120px;
  padding: 16px;
  border: 1px solid #edf2fb;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.82);
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
.feature-item h3,
.timeline-item h3 {
  margin: 0;
  color: #20324a;
  font-size: 15px;
}
.feature-item p,
.timeline-item p,
.action-card p {
  margin: 8px 0 0;
  color: #71839b;
  font-size: 13px;
  line-height: 1.65;
}
.timeline {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.timeline-item {
  display: flex;
  gap: 14px;
  padding: 14px;
  border: 1px solid #edf2fb;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.78);
}
.timeline-index {
  display: grid;
  place-items: center;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  color: #fff;
  border-radius: 14px;
  background: linear-gradient(135deg, #2f8cff, #7d4dff);
  font-weight: 900;
}
.action-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}
.action-card {
  min-height: 140px;
  padding: 18px;
  border: 1px solid #edf2fb;
  border-radius: 20px;
  background:
    radial-gradient(circle at 90% 12%, rgba(47, 140, 255, 0.14), transparent 32%),
    #ffffff;
}
.action-name {
  color: #182a42;
  font-size: 18px;
  font-weight: 900;
}
.action-en {
  margin-top: 5px;
  color: #2f6ce5;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}
.bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
  gap: 18px;
}
.tech-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.tech-list span {
  padding: 10px 14px;
  color: #2f6ce5;
  border: 1px solid #dfe9fb;
  border-radius: 999px;
  background: #f6faff;
  font-size: 13px;
  font-weight: 800;
}
.quick-links {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}
.quick-links button {
  padding: 14px;
  text-align: left;
  border: 1px solid #e3ecfb;
  border-radius: 18px;
  background: #fff;
  cursor: pointer;
  transition: all 0.18s ease;
}
.quick-links button:hover {
  border-color: #9fbfff;
  transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(64, 97, 150, 0.1);
}
.quick-links span {
  display: block;
  color: #20324a;
  font-size: 14px;
  font-weight: 900;
}
.quick-links small {
  display: block;
  margin-top: 6px;
  color: #7b8da5;
  line-height: 1.5;
}

@media (max-width: 1366px) {
  .hero-card,
  .section-grid,
  .bottom-grid {
    grid-template-columns: 1fr;
  }
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .action-grid,
  .quick-links {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .hero-card {
    padding: 24px;
  }
  .hero-content h1 {
    font-size: 28px;
  }
  .feature-grid,
  .overview-grid,
  .action-grid,
  .quick-links {
    grid-template-columns: 1fr;
  }
  .section-heading {
    flex-direction: column;
  }
}
</style>
