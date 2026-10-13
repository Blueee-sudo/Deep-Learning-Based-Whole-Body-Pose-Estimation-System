#!/usr/bin/env python
"""
本地 CPU 小规模冒烟测试：
1) 加载 Django + MMPose 推理链路
2) 从 COCO-WholeBody 中抽样若干图片
3) 执行推理并保存可视化结果
4) 输出运行报告，快速判断代码是否可跑通
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

import cv2


def resolve_image_dir(data_root: Path, split: str) -> Path:
    direct = data_root / split
    nested = data_root / split / split
    if nested.exists():
        return nested
    if direct.exists():
        return direct
    raise FileNotFoundError(f"找不到图片目录: {direct} 或 {nested}")


def collect_images(image_dir: Path) -> list[Path]:
    images: list[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"):
        images.extend(image_dir.rglob(ext))
    return sorted(set(images))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="final_project 本地 CPU 小规模测试")
    parser.add_argument(
        "--project-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="项目根目录，默认自动推断",
    )
    parser.add_argument(
        "--data-root",
        default="",
        help="数据集根目录，默认 <project-root>/coco-wholebody",
    )
    parser.add_argument(
        "--split",
        default="val2017",
        choices=["train2017", "val2017"],
        help="抽样数据集 split，默认 val2017",
    )
    parser.add_argument("--samples", type=int, default=5, help="抽样数量，默认 5")
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="随机种子，默认 42",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "outputs"),
        help="输出目录，默认 final_project_cpu_test/outputs",
    )
    parser.add_argument(
        "--model-name",
        default="",
        help="可选，覆盖模型名；为空则沿用 settings 默认",
    )
    parser.add_argument(
        "--mode",
        default="auto",
        choices=["auto", "full", "lite"],
        help="测试模式：full=真实推理，lite=不加载模型，auto=失败自动降级到lite",
    )
    return parser.parse_args()


def setup_django(project_root: Path, model_name: str) -> None:
    if str(project_root / "backend_django") not in sys.path:
        sys.path.insert(0, str(project_root / "backend_django"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ["MODEL_DEVICE"] = "cpu"
    if model_name.strip():
        os.environ["MODEL_NAME"] = model_name.strip()
    import django  # pylint: disable=import-outside-toplevel

    django.setup()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    data_root = Path(args.data_root).resolve() if args.data_root else (project_root / "coco-wholebody").resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "project_root": str(project_root),
        "data_root": str(data_root),
        "split": args.split,
        "samples": args.samples,
        "device": "cpu",
        "mode": args.mode,
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ok": [],
        "failed": [],
    }

    run_mode = args.mode
    infer_image = None
    draw_pose = None
    if run_mode in ("auto", "full"):
        try:
            setup_django(project_root, args.model_name)
            from apps.pose.services.inferencer import infer_image as infer_image_func  # pylint: disable=import-outside-toplevel
            from apps.pose.services.visualizer import draw_pose as draw_pose_func  # pylint: disable=import-outside-toplevel

            infer_image = infer_image_func
            draw_pose = draw_pose_func
            run_mode = "full"
        except Exception as exc:
            if args.mode == "full":
                report["failed"].append({"stage": "setup", "error": str(exc)})
                (output_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
                print("[FAIL] full 模式初始化失败。")
                print(json.dumps(report, ensure_ascii=False, indent=2))
                return 1
            run_mode = "lite"
            report["fallback_reason"] = str(exc)
            print(f"[WARN] full 模式初始化失败，自动降级为 lite：{exc}")
    report["effective_mode"] = run_mode

    try:
        image_dir = resolve_image_dir(data_root, args.split)
        all_images = collect_images(image_dir)
        if not all_images:
            raise FileNotFoundError(f"目录下没有可用图片: {image_dir}")
        random.seed(args.seed)
        sample_count = min(max(args.samples, 1), len(all_images))
        selected = random.sample(all_images, sample_count)
    except Exception as exc:
        report["failed"].append({"stage": "dataset", "error": str(exc)})
        (output_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("[FAIL] 数据集检查失败。")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    for idx, image_path in enumerate(selected, start=1):
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                raise RuntimeError("cv2.imread 返回 None")
            if run_mode == "full":
                result = infer_image(image)
                vis = draw_pose(image, result["persons"])
                person_count = len(result["persons"])
                infer_ms = result["inference_time_ms"]
            else:
                vis = image.copy()
                cv2.putText(
                    vis,
                    "LITE MODE (no model inference)",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                person_count = -1
                infer_ms = 0.0
            out_path = output_dir / f"{idx:02d}_{image_path.stem}_vis.jpg"
            ok = cv2.imwrite(str(out_path), vis)
            if not ok:
                raise RuntimeError("cv2.imwrite 保存失败")
            report["ok"].append(
                {
                    "image": str(image_path),
                    "output": str(out_path),
                    "person_count": person_count,
                    "inference_time_ms": infer_ms,
                }
            )
            print(
                f"[OK] {idx}/{len(selected)} {image_path.name} "
                f"persons={person_count} time_ms={infer_ms} mode={run_mode}"
            )
        except Exception as exc:
            report["failed"].append({"image": str(image_path), "error": str(exc)})
            print(f"[FAIL] {idx}/{len(selected)} {image_path.name}: {exc}")

    report["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    report["success_count"] = len(report["ok"])
    report["fail_count"] = len(report["failed"])
    report["pass"] = len(report["ok"]) > 0 and len(report["failed"]) == 0

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[REPORT] {summary_path}")
    print(json.dumps({"success": report["success_count"], "failed": report["fail_count"], "pass": report["pass"]}, ensure_ascii=False))
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
