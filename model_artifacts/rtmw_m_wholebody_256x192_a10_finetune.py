"""
RTMW-m whole-body fine-tune config (single A10 24GB, stable-first).

Base config is expected from official MMPose repo:
configs/wholebody_2d_keypoint/rtmpose/cocktail14/rtmw-m_8xb1024-270e_cocktail14-256x192.py

Usage note:
- Put this file under your mmpose repo (e.g. mmpose/my_experiments/)
- Train from mmpose root:
  python tools/train.py my_experiments/rtmw_m_wholebody_256x192_a10_finetune.py
"""

_base_ = [
    "../configs/wholebody_2d_keypoint/rtmpose/cocktail14/rtmw-m_8xb1024-270e_cocktail14-256x192.py"
]

# =========================
# Must-fill fields (server)
# =========================
data_root = "/path/to/coco-wholebody"
load_from = "/path/to/official_rtmw_m_pretrained.pth"
work_dir = "./work_dirs/rtmw_m_wholebody_256x192_a10_ft"

# Dataset annotations/images (COCO-WholeBody)
train_ann_file = "annotations/coco_wholebody_train_v1.0.json"
val_ann_file = "annotations/coco_wholebody_val_v1.0.json"
train_data_prefix = dict(img="train2017/")
val_data_prefix = dict(img="val2017/")

# =========================
# Reproducibility / stability
# =========================
randomness = dict(seed=42, deterministic=False)
env_cfg = dict(cudnn_benchmark=False)

# =========================
# Single A10 conservative setting
# =========================
train_dataloader = dict(
    batch_size=8,
    num_workers=6,
    persistent_workers=True,
    dataset=dict(
        ann_file=train_ann_file,
        data_root=data_root,
        data_prefix=train_data_prefix,
    ),
)
val_dataloader = dict(
    batch_size=8,
    num_workers=4,
    persistent_workers=True,
    dataset=dict(
        ann_file=val_ann_file,
        data_root=data_root,
        data_prefix=val_data_prefix,
    ),
)
test_dataloader = val_dataloader

# Finetune target: first formal release config
train_cfg = dict(max_epochs=40, val_interval=1)

# Conservative LR for single-GPU fine-tune
optim_wrapper = dict(
    optimizer=dict(lr=1e-4),
)
auto_scale_lr = dict(enable=False, base_batch_size=1024)

# Save checkpoints frequently enough for safety
default_hooks = dict(
    checkpoint=dict(interval=1, max_keep_ckpts=5, save_best="coco-wholebody/AP", rule="greater"),
    logger=dict(interval=50),
)

# Keep AMP enabled for speed/memory balance on A10
optim_wrapper.update(dict(type="AmpOptimWrapper"))
