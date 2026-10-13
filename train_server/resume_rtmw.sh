#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash train_server/resume_rtmw.sh /workspace/final_project /workspace/final_project/work_dirs/rtmw_m_finetune/latest.pth

WORKSPACE="${1:-/workspace/final_project}"
RESUME_CKPT="${2:-}"
CFG_PATH="${WORKSPACE}/mmpose/configs/custom/rtmw_m_wholebody_finetune_server.py"

if [ -z "${RESUME_CKPT}" ]; then
  echo "[ERROR] Please provide resume checkpoint path."
  echo "Example: bash train_server/resume_rtmw.sh /workspace/final_project /workspace/final_project/work_dirs/rtmw_m_finetune/latest.pth"
  exit 1
fi

cd "${WORKSPACE}"
source .venv/bin/activate

python "${WORKSPACE}/mmpose/tools/train.py" "${CFG_PATH}" --resume "${RESUME_CKPT}"
