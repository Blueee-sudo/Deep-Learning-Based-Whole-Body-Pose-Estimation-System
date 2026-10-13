import os
from pathlib import Path

import pymysql

pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",
    "corsheaders",
    "rest_framework",
    "apps.pose",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "pose_system"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = False

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = True

# 项目根目录（backend_django 的上一级）
PROJECT_ROOT = BASE_DIR.parent
_DEFAULT_MODEL_CONFIG = PROJECT_ROOT / "model_artifacts" / "rtmw_m_wholebody_256x192_a10_finetune.py"
_DEFAULT_MODEL_CHECKPOINT = PROJECT_ROOT / "model_artifacts" / "best_coco-wholebody_AP_epoch_1.pth"

# MMPose 推理：微调配置文件路径 + epoch1 最优权重（见第 3 章表 3-3）
MODEL_NAME = os.getenv("MODEL_NAME", str(_DEFAULT_MODEL_CONFIG))
MODEL_CHECKPOINT = os.getenv("MODEL_CHECKPOINT", str(_DEFAULT_MODEL_CHECKPOINT))
# 写入检测记录、接口返回的模型标识（与 MODEL_NAME 配置路径区分）
MODEL_DISPLAY_NAME = os.getenv("MODEL_DISPLAY_NAME", "RTMW-M-WholeBody")
MODEL_DEVICE = os.getenv("MODEL_DEVICE", "cuda:0")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.3"))
# 视频抽帧间隔：1=每帧推理，2=每2帧推理一次，3=每3帧推理一次
VIDEO_INFER_FRAME_STRIDE = max(1, int(os.getenv("VIDEO_INFER_FRAME_STRIDE", "2")))

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
