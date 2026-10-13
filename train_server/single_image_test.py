#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from mmpose.apis import inference_topdown, init_model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()

    img = cv2.imread(args.image)
    if img is None:
        raise FileNotFoundError(args.image)

    model = init_model(args.config, args.checkpoint, device=args.device)
    h, w = img.shape[:2]
    bboxes = np.array([[0, 0, w - 1, h - 1]], dtype=np.float32)
    preds = inference_topdown(model, img, bboxes)
    if len(preds) > 0:
        keypoints = preds[0].pred_instances.keypoints[0]
        for x, y in keypoints:
            if x > 0 and y > 0:
                cv2.circle(img, (int(x), int(y)), 1, (0, 255, 0), -1)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), img)
    print(f"[OK] saved: {out}")
    print(f"[OK] num_persons: {len(preds)}")


if __name__ == "__main__":
    main()
