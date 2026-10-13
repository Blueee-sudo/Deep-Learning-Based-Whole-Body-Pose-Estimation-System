#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash train_server/setup_env_aliyun.sh /workspace
#
# Result:
#   - Create venv at <WORKSPACE>/.venv
#   - Install fixed versions for stable RTMW + MMPose finetuning
#   - Clone mmpose v1.3.2 into <WORKSPACE>/mmpose (if not exists)

WORKSPACE="${1:-/workspace/final_project}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[INFO] WORKSPACE=${WORKSPACE}"
mkdir -p "${WORKSPACE}"
cd "${WORKSPACE}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "[ERROR] ${PYTHON_BIN} not found."
  exit 1
fi

${PYTHON_BIN} -m venv .venv
source .venv/bin/activate

python -m pip install -U pip setuptools wheel

# Stable combo requested by user
python -m pip install -U numpy==1.24.4
python -m pip install -U --index-url https://download.pytorch.org/whl/cu121 torch==2.1.2 torchvision==0.16.2
python -m pip install -U mmengine==0.10.7
python -m pip install -U --only-binary=:all: mmcv==2.1.0 -f https://download.openmmlab.com/mmcv/dist/cu121/torch2.1/index.html

# MMPose (without mmdet)
if [ ! -d "mmpose" ]; then
  git clone https://github.com/open-mmlab/mmpose.git
fi
cd mmpose
git fetch --tags
git checkout v1.3.2
python -m pip install -e .
python -m pip install -U mmpose==1.3.2
cd "${WORKSPACE}"

# COCO-WholeBody evaluation dependency with fallback
if ! python -m pip install -U xtcocotools; then
  echo "[WARN] xtcocotools wheel install failed, fallback to source build"
  sudo apt-get update -y
  sudo apt-get install -y build-essential python3-dev
  rm -rf cocoapi
  git clone https://github.com/cocodataset/cocoapi.git
  cd cocoapi/PythonAPI
  python -m pip install -e .
  cd "${WORKSPACE}"
fi

python - <<'PY'
import torch, mmcv, mmengine, mmpose
print("[OK] torch", torch.__version__)
print("[OK] mmcv", mmcv.__version__)
print("[OK] mmengine", mmengine.__version__)
print("[OK] mmpose", mmpose.__version__)
print("[OK] CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("[OK] GPU:", torch.cuda.get_device_name(0))
PY

echo "[DONE] Environment is ready at ${WORKSPACE}/.venv"
