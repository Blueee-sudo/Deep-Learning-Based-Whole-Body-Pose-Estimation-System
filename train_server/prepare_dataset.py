import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    h, w = img.shape[:2]
    center = (w / 2, h / 2)
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def scale_image(img: np.ndarray, ratio: float) -> np.ndarray:
    h, w = img.shape[:2]
    nh, nw = max(8, int(h * ratio)), max(8, int(w * ratio))
    scaled = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(scaled, (w, h), interpolation=cv2.INTER_LINEAR)


def center_crop(img: np.ndarray, crop_ratio: float) -> np.ndarray:
    h, w = img.shape[:2]
    ch, cw = max(8, int(h * crop_ratio)), max(8, int(w * crop_ratio))
    y1 = max(0, (h - ch) // 2)
    x1 = max(0, (w - cw) // 2)
    crop = img[y1 : y1 + ch, x1 : x1 + cw]
    return cv2.resize(crop, (w, h), interpolation=cv2.INTER_LINEAR)


def normalize_and_resize(img: np.ndarray, size: int) -> np.ndarray:
    resized = cv2.resize(img, (size, size), interpolation=cv2.INTER_LINEAR)
    norm = resized.astype(np.float32) / 255.0
    return (norm * 255.0).clip(0, 255).astype(np.uint8)


def augment_variants(img: np.ndarray) -> dict:
    return {
        "orig": img,
        "rot_p15": rotate_image(img, 15.0),
        "rot_n15": rotate_image(img, -15.0),
        "scale_110": scale_image(img, 1.1),
        "scale_090": scale_image(img, 0.9),
        "crop_090": center_crop(img, 0.9),
    }


def main():
    parser = argparse.ArgumentParser(description="数据清洗与增强：旋转/缩放/裁剪/归一化/统一尺寸")
    parser.add_argument("--input-dir", required=True, help="原始图片目录")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--size", type=int, default=256, help="统一输出尺寸，默认 256")
    parser.add_argument("--ext", default="jpg", choices=["jpg", "png", "jpeg"], help="输出格式")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_paths = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"):
        image_paths.extend(input_dir.rglob(ext))
    image_paths = sorted(set(image_paths))

    manifest = []
    for path in image_paths:
        img = cv2.imread(str(path))
        if img is None:
            continue
        base = path.stem
        variants = augment_variants(img)
        for tag, v in variants.items():
            out = normalize_and_resize(v, args.size)
            out_name = f"{base}_{tag}.{args.ext}"
            out_path = output_dir / out_name
            ok = cv2.imwrite(str(out_path), out)
            if ok:
                manifest.append(
                    {
                        "src": str(path),
                        "variant": tag,
                        "output": str(out_path),
                        "size": args.size,
                    }
                )

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"processed={len(manifest)} images, manifest={manifest_path}")


if __name__ == "__main__":
    main()
