"""
离线推理与可视化脚本（不依赖 Web API）。
用于替代原先把推理逻辑放在接口层的做法，直接调用模型服务层。
"""

import argparse
import os
import sys

import cv2

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402

django.setup()

from apps.pose.services.inferencer import infer_image  # noqa: E402
from apps.pose.services.visualizer import draw_pose  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="输入图片路径")
    parser.add_argument("--output", default="outputs/result.jpg", help="输出图片路径")
    return parser.parse_args()


def main():
    args = parse_args()
    image = cv2.imread(args.input)
    if image is None:
        raise FileNotFoundError(f"无法读取输入图片: {args.input}")

    result = infer_image(image)
    vis = draw_pose(image, result["persons"])

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    cv2.imwrite(args.output, vis)
    print(
        {
            "output": args.output,
            "person_count": len(result["persons"]),
            "inference_time_ms": result["inference_time_ms"],
        }
    )


if __name__ == "__main__":
    main()
