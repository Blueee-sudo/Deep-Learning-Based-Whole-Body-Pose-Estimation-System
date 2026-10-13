#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

from mmengine.config import Config


def resolve_img_dir(root: Path, split: str) -> Path:
    direct = root / split
    nested = root / split / split
    if nested.exists():
        return nested
    if direct.exists():
        return direct
    raise FileNotFoundError(f"Cannot find image dir: {direct} or {nested}")


def find_rtmw_config(mmpose_dir: Path, model_size: str, img_size: str) -> Path:
    cfg_root = mmpose_dir / "configs"
    size_patterns = {
        "m": [f"**/rtmw*m*{img_size}*.py", f"**/rtmw*l*{img_size}*.py", f"**/rtmw*{img_size}*.py"],
        "l": [f"**/rtmw*l*{img_size}*.py", f"**/rtmw*m*{img_size}*.py", f"**/rtmw*{img_size}*.py"],
        "auto": [f"**/rtmw*{img_size}*.py", f"**/rtmw*m*{img_size}*.py", f"**/rtmw*l*{img_size}*.py"],
    }
    patterns = size_patterns.get(model_size, size_patterns["m"])
    candidates: list[str] = []
    for pat in patterns:
        candidates.extend(glob.glob(str(cfg_root / pat), recursive=True))
    candidates = [c for c in candidates if "base" not in Path(c).name.lower()]
    if not candidates:
        raise FileNotFoundError(f"No RTMW config found for model_size={model_size}, img_size={img_size}")
    return Path(sorted(candidates)[0])


def patch_dataset(ds, ann_file: Path, img_dir: Path) -> None:
    if hasattr(ds, "dataset"):
        ds = ds.dataset
    ds.ann_file = str(ann_file)
    if hasattr(ds, "data_prefix"):
        ds.data_prefix = dict(img=str(img_dir))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True, help="e.g. /workspace/final_project")
    parser.add_argument("--data-root", required=True, help="e.g. /workspace/final_project/coco-wholebody")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--max-epochs", type=int, default=12)
    parser.add_argument("--model-size", default="m", choices=["m", "l", "auto"])
    parser.add_argument("--img-size", default="256x192")
    parser.add_argument("--val-interval", type=int, default=1)
    parser.add_argument("--checkpoint-interval", type=int, default=1)
    parser.add_argument("--max-keep-ckpts", type=int, default=3)
    parser.add_argument("--work-dir", default="")
    parser.add_argument("--load-from", default="")
    parser.add_argument("--require-load-from", action="store_true", help="Fail if no pretrained checkpoint provided/found")
    parser.add_argument("--amp", action="store_true", help="Enable AmpOptimWrapper")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    mmpose_dir = workspace / "mmpose"
    data_root = Path(args.data_root).resolve()
    ann_dir = data_root / "annotations"
    train_ann = ann_dir / "coco_wholebody_train_v1.0.json"
    val_ann = ann_dir / "coco_wholebody_val_v1.0.json"
    if not train_ann.exists() or not val_ann.exists():
        raise FileNotFoundError(
            "Missing COCO-WholeBody annotations. Need:\n"
            f" - {train_ann}\n - {val_ann}"
        )
    train_img = resolve_img_dir(data_root, "train2017")
    val_img = resolve_img_dir(data_root, "val2017")

    base_cfg = find_rtmw_config(mmpose_dir, args.model_size, args.img_size)
    cfg = Config.fromfile(str(base_cfg))

    cfg.data_root = str(data_root)
    if hasattr(cfg, "train_dataloader"):
        cfg.train_dataloader.batch_size = args.batch_size
        cfg.train_dataloader.num_workers = args.num_workers
        patch_dataset(cfg.train_dataloader.dataset, train_ann, train_img)
    if hasattr(cfg, "val_dataloader"):
        cfg.val_dataloader.num_workers = args.num_workers
        patch_dataset(cfg.val_dataloader.dataset, val_ann, val_img)
    if hasattr(cfg, "test_dataloader"):
        cfg.test_dataloader.num_workers = args.num_workers
        patch_dataset(cfg.test_dataloader.dataset, val_ann, val_img)

    if hasattr(cfg, "train_cfg"):
        cfg.train_cfg.max_epochs = args.max_epochs
        cfg.train_cfg.val_interval = args.val_interval
    if hasattr(cfg, "default_hooks") and hasattr(cfg.default_hooks, "checkpoint"):
        cfg.default_hooks.checkpoint.interval = args.checkpoint_interval
        cfg.default_hooks.checkpoint.max_keep_ckpts = args.max_keep_ckpts
    if args.amp and hasattr(cfg, "optim_wrapper"):
        cfg.optim_wrapper.type = "AmpOptimWrapper"

    cfg.randomness = dict(seed=42)
    cfg.work_dir = args.work_dir or str(workspace / "work_dirs" / f"rtmw_{args.model_size}_finetune")

    if args.load_from.strip():
        cfg.load_from = args.load_from.strip()
    load_from = str(getattr(cfg, "load_from", "") or "").strip()
    if args.require_load_from and not load_from:
        raise ValueError(
            "Pretrained checkpoint is required for first-round fine-tune. "
            "Please pass --load-from (or env LOAD_FROM in train_rtmw.sh)."
        )

    custom_dir = mmpose_dir / "configs" / "custom"
    custom_dir.mkdir(parents=True, exist_ok=True)
    out_cfg = custom_dir / f"rtmw_{args.model_size}_wholebody_finetune_server.py"
    cfg.dump(str(out_cfg))

    summary = {
        "base_config": str(base_cfg),
        "custom_config": str(out_cfg),
        "data_root": str(data_root),
        "train_ann": str(train_ann),
        "val_ann": str(val_ann),
        "train_img": str(train_img),
        "val_img": str(val_img),
        "work_dir": cfg.work_dir,
        "model_size": args.model_size,
        "img_size": args.img_size,
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "max_epochs": args.max_epochs,
        "load_from": load_from,
        "require_load_from": bool(args.require_load_from),
        "amp": bool(args.amp),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
