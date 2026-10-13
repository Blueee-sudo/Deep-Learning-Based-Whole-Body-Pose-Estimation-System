import logging
import time
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

_inferencer_instance: Optional[object] = None


def _resolve_local_path(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return value
    candidate = Path(value)
    if candidate.exists():
        return str(candidate.resolve())
    # backend_django/config/settings.py => BASE_DIR is backend_django
    # project root is BASE_DIR.parent
    base_dir = Path(settings.BASE_DIR)
    project_root = base_dir.parent
    for root in (project_root, base_dir):
        p = (root / value).resolve()
        if p.exists():
            return str(p)
    return value


def _resolve_mmpose_builtin_base(config_path: str) -> str:
    """Patch config `_base_` path when training config is outside mmpose repo.

    This enables using files like `model_artifacts/xxx.py` whose `_base_` is
    `../configs/...`, by remapping it to packaged `mmpose/.mim/configs/...`.
    """
    try:
        cfg_path = Path(config_path)
        if not cfg_path.exists() or cfg_path.suffix != ".py":
            return config_path

        content = cfg_path.read_text(encoding="utf-8")
        if "../configs/" not in content and "./configs/" not in content:
            return config_path

        import mmpose  # type: ignore

        mim_configs = (Path(mmpose.__file__).resolve().parent / ".mim" / "configs")
        if not mim_configs.exists():
            return config_path

        base_root = mim_configs.as_posix()
        patched = content.replace("../configs/", f"{base_root}/")
        patched = patched.replace("./configs/", f"{base_root}/")
        if patched == content:
            return config_path

        tmp_dir = Path(tempfile.gettempdir()) / "pose_system_runtime_cfg"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        runtime_cfg = tmp_dir / f"{cfg_path.stem}_runtime.py"
        runtime_cfg.write_text(patched, encoding="utf-8")
        logger.info("Patched mmpose config for runtime base: %s -> %s", cfg_path, runtime_cfg)
        return str(runtime_cfg)
    except Exception:
        # Non-fatal: keep original path and let mmpose raise detailed errors.
        return config_path


def _flatten_numbers(value):
    if isinstance(value, np.ndarray):
        value = value.tolist()
    if isinstance(value, (list, tuple)):
        out = []
        for item in value:
            out.extend(_flatten_numbers(item))
        return out
    try:
        return [float(value)]
    except Exception:
        return []


def _get_inferencer():
    global _inferencer_instance
    if _inferencer_instance is None:
        try:
            try:
                from mmpose.apis import MMPoseInferencer as PoseInferencer  # type: ignore
            except Exception:
                from mmpose.apis import PoseInferencer  # type: ignore

            pose2d_model = _resolve_local_path(settings.MODEL_NAME)
            pose2d_model = _resolve_mmpose_builtin_base(pose2d_model)
            pose2d_weights = _resolve_local_path(getattr(settings, "MODEL_CHECKPOINT", ""))
            if not pose2d_weights or not Path(pose2d_weights).is_file():
                raise FileNotFoundError(
                    "未找到微调权重文件（MODEL_CHECKPOINT）。"
                    "请设置环境变量指向 best_coco-wholebody_AP_epoch_1.pth，"
                    "例如 model_artifacts/best_coco-wholebody_AP_epoch_1.pth。"
                    f"当前值: {getattr(settings, 'MODEL_CHECKPOINT', '')!r}"
                )
            _inferencer_instance = PoseInferencer(
                pose2d=pose2d_model,
                pose2d_weights=pose2d_weights,
                device=settings.MODEL_DEVICE,
            )
            logger.info(
                "MMPose inferencer initialized (fine-tuned weights): model=%s checkpoint=%s device=%s",
                pose2d_model,
                pose2d_weights,
                settings.MODEL_DEVICE,
            )
        except Exception as e:
            # 记录完整栈，便于本机排查；前端会收到「详情」便于对照环境变量与依赖
            logger.exception("MMPose 初始化失败: %s", e)
            raise RuntimeError(
                f"MMPose 初始化失败，请检查依赖与模型配置。详情：{type(e).__name__}: {e}"
            ) from e
    return _inferencer_instance


def infer_image(image: np.ndarray) -> dict:
    inferencer = _get_inferencer()
    h, w = image.shape[:2]
    t0 = time.perf_counter()
    raw_results = list(inferencer(image, return_vis=False, show=False))
    elapsed_ms = (time.perf_counter() - t0) * 1000

    persons = []
    try:
        preds_list = raw_results[0]["predictions"][0]
    except Exception:
        preds_list = []

    for pred in preds_list:
        kps = np.array(pred.get("keypoints", []))
        scores = np.array(pred.get("keypoint_scores", []))
        if kps.ndim != 2 or kps.shape[0] == 0:
            continue

        bbox = pred.get("bbox", [[0, 0, w, h]])
        bbox = _flatten_numbers(bbox)
        if len(bbox) < 4:
            bbox = [0.0, 0.0, float(w), float(h)]

        keypoints_with_score = np.concatenate([kps, scores[:, np.newaxis]], axis=1).tolist()
        keypoints_filtered = [
            [x, y, s] if s >= settings.CONFIDENCE_THRESHOLD else [0.0, 0.0, 0.0]
            for x, y, s in keypoints_with_score
        ]
        bbox_out = bbox[:5] if len(bbox) >= 5 else bbox[:4] + [1.0]
        persons.append({"bbox": bbox_out, "keypoints": keypoints_filtered})

    return {
        "persons": persons,
        "image_size": {"width": w, "height": h},
        "inference_time_ms": round(elapsed_ms, 2),
    }
