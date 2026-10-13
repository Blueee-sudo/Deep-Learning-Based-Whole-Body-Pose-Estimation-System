#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash train_server/train_rtmw.sh /workspace/final_project /workspace/final_project/coco-wholebody

WORKSPACE="${1:-/workspace/final_project}"
DATA_ROOT="${2:-/workspace/final_project/coco-wholebody}"
RTMW_SIZE="${RTMW_SIZE:-m}"        # m / l / auto
IMG_SIZE="${IMG_SIZE:-256x192}"    # first round: 256x192
BATCH_SIZE="${BATCH_SIZE:-4}"      # first round: smaller and stable
NUM_WORKERS="${NUM_WORKERS:-4}"
MAX_EPOCHS="${MAX_EPOCHS:-12}"
USE_AMP="${USE_AMP:-1}"          # 1 enable, 0 disable
LOAD_FROM="${LOAD_FROM:-}"       # recommended official pretrained checkpoint path/url
REQUIRE_PRETRAIN="${REQUIRE_PRETRAIN:-1}"  # 1 require load_from in generated config
WORK_DIR="${WORK_DIR:-}"         # optional
GPU_ID="${GPU_ID:-0}"            # single-card default

cd "${WORKSPACE}"
source .venv/bin/activate

# Run precheck first to fail early on missing data/config/deps.
bash train_server/precheck_train_env.sh "${WORKSPACE}" "${DATA_ROOT}"

if [ "${REQUIRE_PRETRAIN}" = "1" ]; then
  if [ -z "${LOAD_FROM}" ]; then
    echo "[ERROR] REQUIRE_PRETRAIN=1 but LOAD_FROM is empty."
    echo "        Please set official pretrained checkpoint path/url, e.g.:"
    echo "        LOAD_FROM=/workspace/checkpoints/<official_rtmw_pretrained>.pth"
    exit 1
  fi
  if [[ ! "${LOAD_FROM}" =~ ^https?:// ]] && [ ! -f "${LOAD_FROM}" ]; then
    echo "[ERROR] LOAD_FROM is not a valid local file: ${LOAD_FROM}"
    echo "        If using URL, pass full http(s) link."
    exit 1
  fi
fi

AMP_FLAG=""
if [ "${USE_AMP}" = "1" ]; then
  AMP_FLAG="--amp"
fi

REQUIRE_FLAG=""
if [ "${REQUIRE_PRETRAIN}" = "1" ]; then
  REQUIRE_FLAG="--require-load-from"
fi

python train_server/prepare_rtmw_config.py \
  --workspace "${WORKSPACE}" \
  --data-root "${DATA_ROOT}" \
  --model-size "${RTMW_SIZE}" \
  --img-size "${IMG_SIZE}" \
  --batch-size "${BATCH_SIZE}" \
  --num-workers "${NUM_WORKERS}" \
  --max-epochs "${MAX_EPOCHS}" \
  ${WORK_DIR:+--work-dir "${WORK_DIR}"} \
  ${LOAD_FROM:+--load-from "${LOAD_FROM}"} \
  ${REQUIRE_FLAG} \
  ${AMP_FLAG}

CFG_PATH="${WORKSPACE}/mmpose/configs/custom/rtmw_${RTMW_SIZE}_wholebody_finetune_server.py"
echo "[INFO] First-round preset: size=${RTMW_SIZE}, img=${IMG_SIZE}, batch=${BATCH_SIZE}, amp=${USE_AMP}, gpu=${GPU_ID}"
echo "[INFO] Training config: ${CFG_PATH}"
CUDA_VISIBLE_DEVICES="${GPU_ID}" python "${WORKSPACE}/mmpose/tools/train.py" "${CFG_PATH}"
