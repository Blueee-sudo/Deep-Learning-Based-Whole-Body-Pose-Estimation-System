# 全身姿态关键点定位与动作评估系统

基于 **Django + Vue 3 + Element Plus** 的 Web 应用：在 WholeBody（133 关键点）姿态估计结果之上，完成动作几何分析、可选的大模型评分、历史记录与趋势可视化；支持图片、视频与实时摄像头三类检测入口，并提供管理员控制台。

---

## 1. 功能概览

### 1.1 用户侧

| 能力 | 说明 |
|------|------|
| 注册 / 登录 | JWT 鉴权；统一认证入口 `/auth`（含登录与注册 Tab） |
| 首页 | 系统能力介绍与快捷入口 |
| 图片检测 | 上传图片，选择动作类型，推理、可视化、评分展示、结果图下载 |
| 视频姿态检测 | 上传视频，抽帧间隔配置，异步任务与进度轮询，结果视频下载 |
| 实时检测 | WebSocket 优先，HTTP 帧推理回退；摄像头画面与骨架叠加 |
| 检测历史 | 筛选、分页、详情、删除；**CSV / Excel 导出**（需携带登录 Token，由前端请求触发下载） |
| 动作历史 | 按动作类型筛选的评分与指标摘要 |
| 趋势分析 | ECharts：评分与关键指标趋势 |
| 个人信息 | `GET/PUT /api/auth/me/`（邮箱、头像等，以实际接口为准） |

### 1.2 支持的动作类型（`action_type`）

后端统一集合：`squat`、`plank`、`pushup`、`glute_bridge`、`situp`。

| 值 | 含义 |
|----|------|
| `squat` | 深蹲 |
| `plank` | 平板支撑 |
| `pushup` | 俯卧撑 |
| `glute_bridge` | 臀桥 |
| `situp` | 仰卧起坐 |

图片/视频推理请求中传入 `action_type`；未识别或非法值时后端会回退为默认动作（与 `views.py` 中 `_normalize_action_type` 行为一致）。

### 1.3 管理员（`role_id === 1`）

- 用户列表（可按角色筛选）、检测记录、操作日志、模型指标列表与指标趋势图。
- **普通用户 CRUD**：创建、查看、更新、删除普通用户（不可对管理员账号执行删除等敏感操作，详见后端实现）。

---

## 2. 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3、Vue Router、Vite 6、Element Plus、Axios、ECharts、`@element-plus/icons-vue` |
| 后端 | Django 5、Django REST framework、Channels（WebSocket）、django-cors-headers |
| 数据 | MySQL（PyMySQL）、Django ORM |
| 推理与视觉 | MMPose、MMCV、MMEngine、MMDet、OpenCV、NumPy |
| 安全与认证 | `python-jose`（JWT）、`passlib[bcrypt]` |
| 其它 | `openpyxl`（Excel 导出）、`matplotlib` + `seaborn`（管理员指标图） |
| 评分（可选） | 豆包等兼容 OpenAI 风格的 HTTP API（失败时有结构化兜底） |

---

## 3. 仓库目录结构（核心）

```text
final_project/
├── backend_django/              # Django 工程
│   ├── apps/pose/
│   │   ├── services/          # 推理、可视化、姿态分析、LLM 评分、DB 写入
│   │   ├── views.py           # REST + 部分视图逻辑（鉴权、推理、历史、管理）
│   │   ├── urls.py
│   │   ├── models.py
│   │   ├── consumers.py       # WebSocket 实时推理（若已启用）
│   │   └── management/commands/   # 如 init_pose_system
│   ├── config/                # settings / urls / asgi / wsgi
│   ├── tools/                 # 离线推理脚本等
│   ├── media/                 # 上传与结果文件（运行时生成，勿随意删）
│   ├── requirements.txt
│   └── .env.example             # 环境变量示例（勿提交真实密钥）
├── frontend_vue/               # Vue 3 + Vite
│   ├── src/
│   │   ├── api/               # Axios 封装（含 Bearer Token）
│   │   ├── views/             # 各业务页面
│   │   ├── router.js
│   │   ├── App.vue
│   │   └── stores/
│   ├── vite.config.js         # dev server: host 0.0.0.0，/api 与 /ws 代理到后端
│   └── package.json
├── model_artifacts/            # 模型配置与权重（路径需与环境变量一致）
├── start_all.ps1 / start_all.bat / stop_all.ps1   # Windows 一键启停
├── final_project_cpu_test/   # 可选：本地 CPU 冒烟测试与独立 venv 脚本
├── train_server/             # 可选：训练与数据处理脚本
├── coco-wholebody/           # 可选：数据集（体积大，通常不纳入 Git）
├── workspace/                # 可选：实验输出目录
└── README.md
```

---

## 4. 环境要求

- **操作系统**：Windows 10/11（一键脚本为 PowerShell）
- **Python**：3.10+（与 Django 5 兼容）
- **Node.js**：18+（建议 LTS）
- **MySQL**：8.x（或兼容版本），提前创建数据库用户与库
- **硬件**：CPU 可跑；GPU 需在环境与 `MODEL_DEVICE` 中配置

---

## 5. 安装步骤

### 5.1 后端

```powershell
cd d:\final_project\backend_django
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

复制并编辑环境变量（不要提交含真实密码的 `.env` 到公开仓库）：

```powershell
copy .env.example .env
# 编辑 .env：数据库、SECRET_KEY、模型路径、JWT、豆包 API 等
```

数据库迁移与初始化角色/管理员：

```powershell
python manage.py migrate
python manage.py init_pose_system
```

### 5.2 前端

```powershell
cd d:\final_project\frontend_vue
npm install
```

### 5.3 Excel 导出

历史记录导出 Excel 依赖后端 `openpyxl`；已在 `requirements.txt` 中。若自行精简依赖导致缺失，导出 xlsx 会失败。

---

## 6. 运行方式

### 6.1 一键启动（推荐，Windows）

```powershell
cd d:\final_project
powershell -ExecutionPolicy Bypass -File .\stop_all.ps1
powershell -ExecutionPolicy Bypass -File .\start_all.ps1
```

脚本会打开新窗口分别运行后端（迁移 + `init_pose_system` + `runserver`）与前端（`npm run dev`）。**请勿将 `start_all.ps1` 中的数据库口令、豆包 API Key、管理员密码提交到公共仓库**；生产环境应改为本机环境变量或密钥管理注入。

默认访问：

- 前端开发服务器：`http://localhost:5173`（`vite.config.js` 中 `host: "0.0.0.0"`，局域网可用本机 IPv4 + `:5173` 访问，需放行防火墙）
- 后端 API：`http://127.0.0.1:8000`（与 Vite 代理目标一致）

### 6.2 手动启动

**后端：**

```powershell
cd d:\final_project\backend_django
python manage.py migrate
python manage.py init_pose_system
python manage.py runserver 0.0.0.0:8000
```

**前端：**

```powershell
cd d:\final_project\frontend_vue
npm run dev
```

生产构建：

```powershell
cd d:\final_project\frontend_vue
npm run build
npm run preview
```

---

## 7. 前端路由一览

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | 重定向 | 默认跳到 `/image` |
| `/auth` | 认证入口 | 登录 / 注册 |
| `/login`、`/register` | 旧路由 | 重定向到 `/auth` |
| `/home` | 首页 | 需登录 |
| `/image` | 图片检测 | 需登录 |
| `/video` | 视频姿态检测 | 需登录 |
| `/realtime` | 实时检测 | 需登录 |
| `/history` | 检测历史 | 需登录 |
| `/pose-history` | 动作历史 | 需登录 |
| `/pose-trends` | 趋势分析 | 需登录 |
| `/admin` | 管理员 | 需登录且管理员角色 |

---

## 8. 后端 API 摘要

前缀均为 `/api/`（开发模式下由 Vite 代理到 Django）。

### 认证

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/auth/me/`、`PUT /api/auth/me/`

### 姿态推理

- `POST /api/pose/image/`（`multipart`：`file`、`action_type`）
- `GET /api/pose/image/{detection_id}/result/`
- `POST /api/pose/video/`（视频 + `frame_stride` 等）
- `GET /api/pose/video/{detection_id}/progress/`
- `GET /api/pose/video/{detection_id}/result/`
- `POST /api/pose/realtime/frame/`（Base64 帧，HTTP 回退场景）
- WebSocket：`/ws/...`（以 `routing.py` 与实际前端连接为准）

### 历史与动作

- `GET /api/history/`（分页与筛选参数与前端一致）
- `GET /api/history/export/?fmt=csv|excel`（需 **Authorization: Bearer**；筛选参数可与列表一致）
- `GET /api/history/{detection_id}/`
- `DELETE /api/history/{detection_id}/delete/`
- `GET /api/pose/history/`（动作历史，`action_type` 可选）

### 管理员

- `GET /api/admin/users/`、`POST /api/admin/users/`（创建普通用户）
- `GET|PUT|DELETE /api/admin/users/{user_id}/`（查看 / 更新 / 删除普通用户）
- `GET /api/admin/detections/`
- `GET /api/admin/logs/`
- `GET|POST /api/admin/metrics/`
- `GET /api/admin/metrics/plot/`

---

## 9. 核心代码位置（便于维护）

| 模块 | 路径 | 职责 |
|------|------|------|
| 推理入口 | `apps/pose/services/inferencer.py` | MMPose 整图推理，输出 `persons`、耗时等 |
| 骨架绘制 | `apps/pose/services/visualizer.py` | 133 点可视化叠加 |
| 动作几何分析 | `apps/pose/services/pose_analysis.py` | 五种动作的结构化指标与阶段 |
| LLM 评分 | `apps/pose/services/llm_scoring.py` | 按动作组装提示词，调用外部 API，失败兜底 |
| 持久化摘要 | `apps/pose/services/db_service.py` | 检测记录、关键点、动作结果与指标摘要 |
| HTTP API | `apps/pose/views.py` | 鉴权、业务聚合、管理员用户管理等 |
| 前端 API | `frontend_vue/src/api/*.js` | 与后端路径、方法对齐 |

---

## 10. 配置说明（环境变量）

在 `backend_django/config/settings.py` 及业务代码中会读取的典型变量包括：

- **数据库**：`DB_HOST`、`DB_PORT`、`DB_NAME`、`DB_USER`、`DB_PASSWORD`
- **模型**：`MODEL_NAME`（RTMW-M 微调配置文件路径）、`MODEL_CHECKPOINT`（如 `best_coco-wholebody_AP_epoch_1.pth`）、`MODEL_DISPLAY_NAME`（记录用标识）、`MODEL_DEVICE`、`CONFIDENCE_THRESHOLD`
- **视频**：`VIDEO_INFER_FRAME_STRIDE`
- **JWT**：`JWT_SECRET_KEY`、`JWT_ALGORITHM`、`JWT_EXPIRE_MINUTES`
- **评分服务**：`DOUBAO_API_KEY`、`DOUBAO_MODEL`、`DOUBAO_BASE_URL`、`DOUBAO_TIMEOUT`（名称以代码为准）
- **初始化管理员**：`INIT_ADMIN_USERNAME`、`INIT_ADMIN_EMAIL`、`INIT_ADMIN_PASSWORD`（仅初始化脚本使用）

完整示例以 `.env.example` 与 `settings.py` 为准。

---

## 11. 辅助与扩展

### 11.1 离线单图推理（示例）

```powershell
cd d:\final_project\backend_django
python tools\offline_infer_and_visualize.py --input demo.jpg --output outputs\demo_result.jpg
```

### 11.2 CPU 冒烟测试

```powershell
cd d:\final_project
python final_project_cpu_test\run_cpu_smoke_test.py --samples 5
```

详见 `final_project_cpu_test/README.md`。

### 11.3 训练脚本

`train_server/` 下为服务器侧训练、数据与验证相关脚本，与主站运行无强耦合。

---

## 12. 常见问题

1. **手机无法访问电脑上的 `http://IP:5173`**  
   换热点后 IP 会变化；用 `ipconfig` 查看当前 IPv4。若电脑可访问而手机不可，检查 Windows 防火墙是否放行 TCP `5173`。部分手机开热点时限制终端互访，可改为电脑开热点或同一路由器 Wi-Fi。

2. **导出 CSV/Excel 无反应**  
   导出必须由带 Token 的前端请求触发（不能直接粘贴无 Cookie 的浏览器地址）。若 Excel 报错，确认已安装 `openpyxl`。

3. **视频无法处理**  
   优先使用 H.264 编码的 MP4，降低 OpenCV 解码失败概率。

4. **评分一直为兜底文案**  
   检查豆包相关环境变量、网络与配额；未配置时系统仍可演示几何分析部分。

---

## 13. 安全与仓库卫生

- 不要将 **生产数据库密码、JWT 密钥、第三方 API Key** 写入 Git 跟踪文件。
- `node_modules`、`dist`、Python `__pycache__`、本地 `.venv` 等应由 `.gitignore` 排除（若尚未配置，请补充）。
- 超大数据集（如 `coco-wholebody`）与实验输出（如 `workspace`）建议单独备份，不必纳入版本库。

---

## 14. 文档维护

本 README 与当前主分支功能对齐：**五种动作**、**管理员普通用户管理**、**认证入口 `/auth`**、**历史导出需鉴权** 等。若接口或目录有较大变更，请同步更新本节与上文表格。
