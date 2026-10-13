import statistics
from typing import Optional

from ..models import DetectionHistory, KeypointData, ModelMetrics, OperationLog, PoseAnalysisResult, User


def calc_avg_score(keypoints: list[list[float]], start: int, end: int) -> float:
    scores = [kp[2] for kp in keypoints[start:end] if len(kp) >= 3 and kp[2] > 0.01]
    return round(statistics.mean(scores), 4) if scores else 0.0


def create_detection(
    *,
    user: User,
    input_type: str,
    original_filename: Optional[str] = None,
    file_path: Optional[str] = None,
    model_name: str = "rtmpose-wholebody",
) -> DetectionHistory:
    return DetectionHistory.objects.create(
        user=user,
        input_type=input_type,
        original_filename=original_filename,
        file_path=file_path,
        model_name=model_name,
        status="pending",
    )


def save_keypoints(detection: DetectionHistory, persons: list, frame_index: int = 0) -> int:
    objs = []
    for pi, person in enumerate(persons):
        kps = person.get("keypoints", [])
        bbox = person.get("bbox", [])
        objs.append(
            KeypointData(
                detection=detection,
                person_index=pi,
                frame_index=frame_index,
                keypoints=kps,
                bbox_x1=bbox[0] if len(bbox) > 0 else None,
                bbox_y1=bbox[1] if len(bbox) > 1 else None,
                bbox_x2=bbox[2] if len(bbox) > 2 else None,
                bbox_y2=bbox[3] if len(bbox) > 3 else None,
                bbox_score=bbox[4] if len(bbox) > 4 else None,
                avg_body_score=calc_avg_score(kps, 0, 17) if len(kps) >= 17 else 0.0,
                avg_face_score=calc_avg_score(kps, 23, 91) if len(kps) >= 91 else 0.0,
                avg_hand_score=calc_avg_score(kps, 91, 133) if len(kps) >= 133 else 0.0,
            )
        )
    if objs:
        KeypointData.objects.bulk_create(objs, batch_size=500)
    return len(objs)


def write_op_log(
    *,
    action: str,
    user: Optional[User] = None,
    request_path: Optional[str] = None,
    request_method: Optional[str] = None,
    response_status: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    extra_data: Optional[dict] = None,
) -> None:
    OperationLog.objects.create(
        user=user,
        action=action,
        request_path=request_path,
        request_method=request_method,
        response_status=response_status,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data=extra_data,
    )


def create_metric(payload: dict) -> ModelMetrics:
    return ModelMetrics.objects.create(**payload)


def build_metrics_summary(action_type: str, pose_analysis: dict, pose_score_result: dict) -> dict:
    action = str(action_type or "squat").lower()
    angles = dict((pose_analysis or {}).get("angles") or {})
    symmetry = dict((pose_analysis or {}).get("symmetry") or {})
    alignment = dict((pose_analysis or {}).get("alignment") or {})
    score = (pose_score_result or {}).get("score")

    if action == "plank":
        return {
            "score": score,
            "hip_angle": angles.get("hip_angle"),
            "torso_lean": angles.get("torso_lean"),
            "body_line_deviation": alignment.get("body_line_deviation"),
            "hip_offset": alignment.get("hip_offset"),
            "hip_trend": alignment.get("hip_trend"),
        }

    if action == "pushup":
        return {
            "score": score,
            "elbow_angle": angles.get("elbow_angle"),
            "left_elbow": angles.get("left_elbow"),
            "right_elbow": angles.get("right_elbow"),
            "elbow_diff": symmetry.get("elbow_diff"),
            "torso_lean": angles.get("torso_lean"),
            "body_line_deviation": alignment.get("body_line_deviation"),
            "hip_offset": alignment.get("hip_offset"),
            "hip_trend": alignment.get("hip_trend"),
            "phase": alignment.get("phase"),
        }

    if action == "glute_bridge":
        return {
            "score": score,
            "hip_extension": angles.get("hip_extension"),
            "left_hip": angles.get("left_hip"),
            "right_hip": angles.get("right_hip"),
            "hip_diff": symmetry.get("hip_diff"),
            "knee_angle": angles.get("knee_angle"),
            "knee_diff": symmetry.get("knee_diff"),
            "body_line_deviation": alignment.get("body_line_deviation"),
            "hip_offset": alignment.get("hip_offset"),
            "hip_trend": alignment.get("hip_trend"),
            "phase": alignment.get("phase"),
        }

    if action == "situp":
        return {
            "score": score,
            "hip_flexion": angles.get("hip_flexion"),
            "left_hip": angles.get("left_hip"),
            "right_hip": angles.get("right_hip"),
            "hip_diff": symmetry.get("hip_diff"),
            "knee_angle": angles.get("knee_angle"),
            "knee_diff": symmetry.get("knee_diff"),
            "torso_angle": angles.get("torso_angle"),
            "torso_raise": alignment.get("torso_raise"),
            "phase": alignment.get("phase"),
        }

    return {
        "score": score,
        "left_knee": angles.get("left_knee"),
        "right_knee": angles.get("right_knee"),
        "knee_diff": symmetry.get("knee_diff"),
        "left_hip": angles.get("left_hip"),
        "right_hip": angles.get("right_hip"),
        "hip_diff": symmetry.get("hip_diff"),
        "torso_lean": angles.get("torso_lean"),
    }


def upsert_pose_analysis_result(
    detection: DetectionHistory,
    action_type: str,
    pose_analysis: dict,
    pose_score_result: dict,
) -> PoseAnalysisResult:
    metrics_json = build_metrics_summary(action_type, pose_analysis, pose_score_result)
    defaults = {
        "action_type": str(action_type or "squat").lower(),
        "score": (pose_score_result or {}).get("score"),
        "overall_comment": (pose_score_result or {}).get("overall_comment"),
        "metrics_json": metrics_json,
        "analysis_json": dict(pose_analysis or {}),
    }
    item, _ = PoseAnalysisResult.objects.update_or_create(detection=detection, defaults=defaults)
    return item
