#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash train_server/precheck_train_env.sh /workspace/final_project /workspace/final_project/coco-wholebody

WORKSPACE="${1:-/workspace/final_project}"
DATA_ROOT="${2:-/workspace/final_project/coco-wholebody}"

ANN_DIR="${DATA_ROOT}/annotations"
TRAIN_ANN="${ANN_DIR}/coco_wholebody_train_v1.0.json"
VAL_ANN="${ANN_DIR}/coco_wholebody_val_v1.0.json"
TRAIN_DIR_A="${DATA_ROOT}/train2017"
TRAIN_DIR_B="${DATA_ROOT}/train2017/train2017"
VAL_DIR_A="${DATA_ROOT}/val2017"
VAL_DIR_B="${DATA_ROOT}/val2017/val2017"
VENV_PY="${WORKSPACE}/.venv/bin/python"
MMP_TRAIN="${WORKSPACE}/mmpose/tools/train.py"
MMP_CFG_DIR="${WORKSPACE}/mmpose/configs"

echo "[INFO] workspace: ${WORKSPACE}"
echo "[INFO] data_root : ${DATA_ROOT}"

if [ ! -d "${WORKSPACE}" ]; then
  echo "[ERROR] workspace not found: ${WORKSPACE}"
  exit 1
fi

if [ ! -x "${VENV_PY}" ]; then
  echo "[ERROR] Python venv not found: ${VENV_PY}"
  echo "        Run: bash train_server/setup_env_aliyun.sh ${WORKSPACE}"
  exit 1
fi

if [ ! -f "${TRAIN_ANN}" ]; then
  echo "[ERROR] Missing annotation: ${TRAIN_ANN}"
  exit 1
fi

if [ ! -f "${VAL_ANN}" ]; then
  echo "[ERROR] Missing annotation: ${VAL_ANN}"
  exit 1
fi

if [ ! -d "${TRAIN_DIR_A}" ] && [ ! -d "${TRAIN_DIR_B}" ]; then
  echo "[ERROR] Missing train images dir: ${TRAIN_DIR_A} or ${TRAIN_DIR_B}"
  exit 1
fi

if [ ! -d "${VAL_DIR_A}" ] && [ ! -d "${VAL_DIR_B}" ]; then
  echo "[ERROR] Missing val images dir: ${VAL_DIR_A} or ${VAL_DIR_B}"
  exit 1
fi

if [ ! -f "${MMP_TRAIN}" ]; then
  echo "[ERROR] Missing mmpose train entry: ${MMP_TRAIN}"
  exit 1
fi

if [ ! -d "${MMP_CFG_DIR}" ]; then
  echo "[ERROR] Missing mmpose configs dir: ${MMP_CFG_DIR}"
  exit 1
fi

"${VENV_PY}" - <<'PY'
import importlib.util
mods = ["torch", "mmengine", "mmcv", "mmpose", "xtcocotools"]
missing = []
for m in mods:
    if importlib.util.find_spec(m) is None:
        missing.append(m)
if missing:
    raise SystemExit(f"[ERROR] Missing python packages: {', '.join(missing)}")
print("[OK] Python package check passed")
PY

echo "[OK] Precheck passed. Training can start."
