# Design and Implementation of a Deep Learning-Based Whole-Body Pose Estimation System
[English](README.md) | [简体中文](README.zh-CN.md)
An undergraduate dissertation project integrating **RTMW-M whole-body pose estimation** with a **Django + Vue 3 + Element Plus** web application. The system estimates **133 keypoints**, performs geometric posture analysis for five exercise types, and supports image, video and live-camera pose estimation.

The application also provides optional large language model (LLM) feedback, detection history, trend visualisation and an administrator dashboard.

## Research and Project Highlights

- Fine-tuned a pretrained **RTMW-M** model using **MMPose** on **COCO-WholeBody**, achieving a **validation AP of 0.604** and selecting the best-performing checkpoint for system integration.
- Implemented geometric analysis for **squats, planks, push-ups, glute bridges and sit-ups**, using predicted keypoints to calculate joint angles, assess alignment and symmetry, and generate structured posture feedback for static images.
- Developed a Django–Vue application supporting image, video and live-camera inference, skeleton visualisation, detection history and role-based access control.
- Added optional **Doubao LLM feedback** based on structured geometric analysis. This service is separate from the pose estimation model and is not required for geometric analysis.

> **Repository scope:** Source code, model configurations, training scripts and sample images are included. Dataset files, model weights, local environments and generated runtime files are excluded. Running pose inference requires a compatible model checkpoint, which is not supplied in this repository.

## 1. Features

### 1.1 User Features

| Feature | Description |
| --- | --- |
| Registration and login | JWT authentication through the unified `/auth` page, with login and registration tabs |
| Home page | System introduction and shortcuts to core features |
| Image inference | Image upload, exercise selection, inference, skeleton visualisation, feedback display and result image download |
| Video pose estimation | Video upload, configurable frame sampling, asynchronous processing, progress polling and result video download |
| Live-camera inference | WebSocket-based inference with an HTTP frame-inference fallback, displaying camera frames and skeleton overlays |
| Detection history | Filtering, pagination, detail views, deletion, and CSV/Excel export through authenticated frontend requests |
| Exercise history | Score and metric summaries filtered by exercise type |
| Trend analysis | Score and key metric trends visualised with ECharts |
| Profile management | `GET/PUT /api/auth/me/` for profile fields such as email and avatar, subject to the implemented endpoint |

### 1.2 Supported Exercise Types

The backend supports the following `action_type` values:

| Value | Exercise |
| --- | --- |
| `squat` | Squat |
| `plank` | Plank |
| `pushup` | Push-up |
| `glute_bridge` | Glute bridge |
| `situp` | Sit-up |

Image and video inference requests can include `action_type`. Unrecognised or invalid values fall back to the default exercise, following `_normalize_action_type` in `views.py`.

Image-based posture analysis evaluates the pose visible in an individual image; it does not establish the quality of an entire exercise sequence.

### 1.3 Administrator Features

Administrator access uses `role_id === 1`.

- User lists with role filtering, detection records and operation logs.
- Model metric lists and metric trend plots.
- Creation, viewing, updating and deletion of ordinary users. Restrictions on sensitive operations involving administrator accounts are defined in the backend implementation.

## 2. Technology Stack

| Layer | Technologies |
| --- | --- |
| Frontend | Vue 3, Vue Router, Vite 6, Element Plus, Axios, ECharts, `@element-plus/icons-vue` |
| Backend | Django 5, Django REST framework, Channels, django-cors-headers |
| Database | MySQL, PyMySQL, Django ORM |
| Pose estimation and vision | PyTorch, MMPose, MMCV, MMEngine, MMDetection, OpenCV, NumPy |
| Authentication | `python-jose` for JWT, `passlib[bcrypt]` |
| Export and plotting | `openpyxl`, Matplotlib, Seaborn |
| Optional LLM feedback | Doubao through an OpenAI-style chat completions HTTP API, with structured fallback responses |

## 3. Repository Structure

Paths below are relative to the repository root.

| Path | Purpose |
| --- | --- |
| `backend_django/` | Django backend |
| `backend_django/apps/pose/services/` | Inference, visualisation, geometric analysis, LLM feedback and database services |
| `backend_django/apps/pose/views.py` | Authentication, inference, history and administration endpoints |
| `backend_django/apps/pose/consumers.py` | WebSocket inference handling |
| `backend_django/apps/pose/management/commands/` | Initialisation commands, including `init_pose_system` |
| `backend_django/config/` | Django settings, URL configuration, ASGI and WSGI |
| `backend_django/tools/` | Offline inference utilities |
| `backend_django/requirements.txt` | Backend dependencies |
| `backend_django/.env.example` | Example environment configuration |
| `frontend_vue/` | Vue 3 and Vite frontend |
| `frontend_vue/src/api/` | API clients, including Bearer token handling |
| `frontend_vue/src/views/` | Application pages |
| `frontend_vue/vite.config.js` | Development server and backend proxy configuration |
| `model_artifacts/` | Model configuration and demonstration images; weights are excluded |
| `my_experiments/` | Experiment configuration |
| `train_server/` | Training, environment setup and dataset preparation scripts |
| `final_project_cpu_test/` | CPU smoke-test utilities and setup instructions |
| `start_all.ps1`, `start_all.bat`, `stop_all.ps1` | Windows startup and shutdown scripts |
| `README.md` | Project documentation |

Local directories such as `coco-wholebody/`, `backend_django/media/`, frontend dependencies and CPU test outputs are excluded by `.gitignore`.

## 4. Requirements

- **Operating system:** Windows 10/11 for the provided PowerShell startup scripts.
- **Python:** 3.10 or later, with versions compatible with Django and the selected OpenMMLab stack.
- **Node.js:** A version compatible with Vite 6 and the dependencies in `frontend_vue/package.json`.
- **Database:** MySQL 8.x or a compatible version, with a database and user created before migration.
- **Hardware:** A compatible GPU environment for GPU inference; CPU smoke-test utilities are provided separately.
- **Model checkpoint:** Compatible RTMW-M weights matching the supplied configuration.

PyTorch, CUDA, MMCV, MMEngine, MMPose and MMDetection versions must be compatible with one another. See the environment setup scripts and dependency files for the intended setup.

## 5. Installation

### 5.1 Clone the Repository

```powershell
git clone https://github.com/Blueee-sudo/Deep-Learning-Based-Whole-Body-Pose-Estimation-System.git
cd .\Deep-Learning-Based-Whole-Body-Pose-Estimation-System
```

### 5.2 Backend

From the repository root:

```powershell
cd .\backend_django
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your local database credentials, secret key and model configuration. Do not commit actual credentials.

**Environment loading:** The shared Django settings use `os.getenv(...)`. Creating a `.env` file alone does not load its contents into the process environment. Confirm whether the startup scripts load it; otherwise set the required environment variables in the PowerShell session that launches Django.

For example, replace the placeholders before running:

```powershell
$env:DB_NAME = "pose_system"
$env:DB_USER = "your-database-user"
$env:DB_PASSWORD = "your-local-database-password"
$env:SECRET_KEY = "your-local-secret-key"
$env:ALLOWED_HOSTS = "127.0.0.1,localhost"
```

Before using optional LLM feedback, also configure `DOUBAO_API_KEY` and `DOUBAO_MODEL` in the backend process environment.

Create the database in MySQL, then run:

```powershell
python manage.py migrate
python manage.py init_pose_system
```

Review the initialisation command and set the `INIT_ADMIN_*` variables as required before creating the administrator account.

### 5.3 Model Configuration and Checkpoint

The default configuration is:

```text
model_artifacts/rtmw_m_wholebody_256x192_a10_finetune.py
```

The default checkpoint location is:

```text
model_artifacts/best_coco-wholebody_AP_epoch_1.pth
```

**The checkpoint is excluded from this repository.** Supply the trained checkpoint locally or configure a compatible checkpoint and matching configuration. Evaluation results reported above refer to the project's selected fine-tuned checkpoint.

For custom locations, set `MODEL_NAME` and `MODEL_CHECKPOINT`. Absolute paths avoid ambiguity about the working directory. Set `MODEL_DEVICE` to match the available hardware, such as `cuda:0` or `cpu`.

### 5.4 Frontend

Open another PowerShell terminal at the repository root:

```powershell
cd .\frontend_vue
npm install
```

### 5.5 Excel Export

Excel export requires `openpyxl`, which is included in the backend requirements. Removing it from a customised installation will cause XLSX export to fail.

## 6. Running the Application

### 6.1 Windows Startup Scripts

Run from the repository root after reviewing the scripts and configuring the local environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_all.ps1
```

To stop the application:

```powershell
powershell -ExecutionPolicy Bypass -File .\stop_all.ps1
```

The startup script opens separate windows for the backend and frontend. Its documented workflow includes database migration, account initialisation, Django development-server startup and `npm run dev`.

Do not store actual database passwords, API keys or administrator passwords in tracked startup scripts.

Default development URLs:

| Service | URL |
| --- | --- |
| Frontend | `http://localhost:5173` |
| Backend | `http://127.0.0.1:8000` |

The Vite configuration proxies `/api` and `/ws` requests to the backend. Its `0.0.0.0` host setting permits LAN access when networking and firewall rules allow it.

### 6.2 Manual Startup

In a backend terminal, activate the environment and set the required variables first:

```powershell
cd .\backend_django
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py init_pose_system
python manage.py runserver 127.0.0.1:8000
```

In a separate terminal at the repository root:

```powershell
cd .\frontend_vue
npm run dev
```

To build and preview the frontend:

```powershell
npm run build
npm run preview
```

The preview command previews the frontend build; it does not start the Django backend.

## 7. Frontend Routes

| Path | Page | Access |
| --- | --- | --- |
| `/` | Redirects to `/image` | Subject to authentication guards |
| `/auth` | Login and registration | Authentication entry point |
| `/login`, `/register` | Redirect to `/auth` | Legacy routes |
| `/home` | Home | Login required |
| `/image` | Image inference | Login required |
| `/video` | Video pose estimation | Login required |
| `/realtime` | Live-camera inference | Login required |
| `/history` | Detection history | Login required |
| `/pose-history` | Exercise history | Login required |
| `/pose-trends` | Trend analysis | Login required |
| `/admin` | Administrator dashboard | Administrator login required |

## 8. Backend API Summary

REST endpoints use the `/api/` prefix. During development, frontend requests are proxied by Vite.

### Authentication

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register/` | Register a user |
| POST | `/api/auth/login/` | Log in |
| GET, PUT | `/api/auth/me/` | Retrieve or update the current user's profile |

### Pose Inference

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/pose/image/` | Image inference using multipart `file` and `action_type` |
| GET | `/api/pose/image/{detection_id}/result/` | Retrieve an image result |
| POST | `/api/pose/video/` | Submit a video, with parameters such as `frame_stride` |
| GET | `/api/pose/video/{detection_id}/progress/` | Retrieve processing progress |
| GET | `/api/pose/video/{detection_id}/result/` | Retrieve the video result |
| POST | `/api/pose/realtime/frame/` | HTTP fallback inference using a Base64 frame |

WebSocket routes use `/ws/...`; refer to `routing.py` and the frontend connection code for the exact path.

### History

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/history/` | List detection history with pagination and filtering |
| GET | `/api/history/export/?fmt=csv` | Export CSV |
| GET | `/api/history/export/?fmt=excel` | Export Excel |
| GET | `/api/history/{detection_id}/` | Retrieve a detection record |
| DELETE | `/api/history/{detection_id}/delete/` | Delete a detection record |
| GET | `/api/pose/history/` | Retrieve exercise history, optionally filtered by `action_type` |

Export requests require an `Authorization: Bearer <token>` header. Filtering parameters can match those used for the history list.

### Administration

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET, POST | `/api/admin/users/` | List users or create an ordinary user |
| GET, PUT, DELETE | `/api/admin/users/{user_id}/` | Retrieve, update or delete an ordinary user |
| GET | `/api/admin/detections/` | List detection records |
| GET | `/api/admin/logs/` | List operation logs |
| GET, POST | `/api/admin/metrics/` | Retrieve or add model metrics |
| GET | `/api/admin/metrics/plot/` | Retrieve metric plots |

## 9. Core Implementation

Backend service paths below are relative to `backend_django/`.

| Module | Path | Responsibility |
| --- | --- | --- |
| Inference | `apps/pose/services/inferencer.py` | MMPose inference, person results and timing information |
| Skeleton visualisation | `apps/pose/services/visualizer.py` | Overlay of 133 keypoints |
| Geometric analysis | `apps/pose/services/pose_analysis.py` | Structured exercise metrics and pose-stage analysis for five exercise types |
| Optional LLM feedback | `apps/pose/services/llm_scoring.py` | Exercise-specific prompts, external API calls and fallback handling |
| Persistence | `apps/pose/services/db_service.py` | Detection records, keypoints, analysis results and metric summaries |
| HTTP API | `apps/pose/views.py` | Authentication, inference workflows, history and administration |
| Frontend API | `frontend_vue/src/api/*.js` | Client requests aligned with backend endpoints; path relative to repository root |

## 10. Environment Variables

| Category | Variables |
| --- | --- |
| Django | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` |
| Database | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` |
| Model | `MODEL_NAME`, `MODEL_CHECKPOINT`, `MODEL_DISPLAY_NAME`, `MODEL_DEVICE`, `CONFIDENCE_THRESHOLD` |
| Video sampling | `VIDEO_INFER_FRAME_STRIDE` |
| JWT | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES` |
| Optional feedback | `DOUBAO_API_KEY`, `DOUBAO_MODEL`, `DOUBAO_BASE_URL`, `DOUBAO_TIMEOUT` |
| Account initialisation | `INIT_ADMIN_USERNAME`, `INIT_ADMIN_EMAIL`, `INIT_ADMIN_PASSWORD` |

`MODEL_NAME` specifies the configuration path; `MODEL_DISPLAY_NAME` is the label stored in records. `VIDEO_INFER_FRAME_STRIDE=1` requests inference on every frame, while larger values reduce the sampling frequency.

Use `.env.example`, `settings.py` and the relevant service or initialisation code as references for defaults and supported options.

## 11. Utilities and Training

### 11.1 Offline Image Inference

From `backend_django/`, with the required environment and model configured:

```powershell
python tools\offline_infer_and_visualize.py --input demo.jpg --output outputs\demo_result.jpg
```

Replace the input and output paths as needed.

### 11.2 CPU Smoke Test

From the repository root, after following the CPU environment setup instructions:

```powershell
python final_project_cpu_test\run_cpu_smoke_test.py --samples 5
```

See `final_project_cpu_test/README.md` for setup and test details. Smoke tests check basic execution; they do not replace model evaluation.

### 11.3 Training Scripts

`train_server/` contains server-side environment setup, dataset preparation, configuration generation, training, resume and inference scripts. These utilities are separate from the web application's runtime workflow.

The COCO-WholeBody dataset must be obtained and prepared separately. Training outputs and checkpoints are managed locally rather than included in this repository.

## 12. Troubleshooting

| Issue | Suggested checks |
| --- | --- |
| A phone cannot access the frontend | Verify the computer's current IPv4 address using `ipconfig`, check TCP port 5173 in Windows Firewall, and confirm that both devices can communicate on the network. Some phone hotspots restrict communication between clients. |
| CSV or Excel export does not work | Use the authenticated frontend download request. Opening the endpoint directly may omit the required Bearer token. Check that `openpyxl` is installed for Excel export. |
| Video processing fails | Try an H.264-encoded MP4 and check OpenCV decoding support. |
| Feedback returns a fallback message | Check `DOUBAO_*` environment variables, network access and API quota. Geometric analysis can be demonstrated without the optional LLM service. |
| Model loading fails | Check checkpoint availability, configuration/checkpoint compatibility, resolved paths, installed OpenMMLab versions and `MODEL_DEVICE`. |
| Values in `.env` are not taking effect | Confirm that a startup component loads the file, or set the variables in the backend process environment. `os.getenv` does not load `.env` automatically. |

## 13. Development Configuration and Repository Hygiene

- Keep actual database passwords, JWT secrets and API keys out of tracked code, configuration examples and startup scripts.
- Keep datasets, checkpoints, virtual environments, `node_modules`, build output, caches and runtime media outside version control using `.gitignore`.
- Review changes before committing, particularly scripts and configuration files.
- The provided Django defaults are intended for local development. Public deployment requires appropriate secret management, `DEBUG=False`, restricted hosts and CORS, and a suitable application-server setup.

## 14. Documentation Maintenance

Update this README when routes, configuration, directory structure or behaviour change. The documented functionality includes five exercise types, ordinary-user administration, the unified `/auth` page and authenticated history export.
