import math
from typing import Any, Dict, List, Optional, Tuple

try:
    from django.conf import settings
except Exception:  # pragma: no cover
    settings = None


# COCO-WholeBody keypoint indices used in v1 squat analysis
IDX_LEFT_SHOULDER = 5
IDX_RIGHT_SHOULDER = 6
IDX_LEFT_ELBOW = 7
IDX_RIGHT_ELBOW = 8
IDX_LEFT_WRIST = 9
IDX_RIGHT_WRIST = 10
IDX_LEFT_HIP = 11
IDX_RIGHT_HIP = 12
IDX_LEFT_KNEE = 13
IDX_RIGHT_KNEE = 14
IDX_LEFT_ANKLE = 15
IDX_RIGHT_ANKLE = 16


def _default_result(reason: str = "", selected: bool = False) -> Dict[str, Any]:
    return {
        "action_type": "squat",
        "scoring_scope": "main_person_only",
        "main_person_selected": selected,
        "angles": {
            "left_knee": 0.0,
            "right_knee": 0.0,
            "left_hip": 0.0,
            "right_hip": 0.0,
            "torso_lean": 0.0,
        },
        "symmetry": {
            "knee_diff": 0.0,
            "hip_diff": 0.0,
        },
        "confidence_summary": {
            "min_score_used": 0.0,
            "required_points": 8,
            "valid_required_points": 0,
            "avg_required_score": 0.0,
        },
        "validity": {
            "enough_keypoints": False,
            "reason": reason,
        },
    }


def _default_plank_result(reason: str = "", selected: bool = False) -> Dict[str, Any]:
    return {
        "action_type": "plank",
        "scoring_scope": "main_person_only",
        "main_person_selected": selected,
        "angles": {
            "hip_angle": 0.0,
            "torso_lean": 0.0,
        },
        "alignment": {
            "body_line_deviation": 0.0,
            "hip_offset": 0.0,
            "hip_trend": "normal",
        },
        "confidence_summary": {
            "min_score_used": 0.0,
            "required_points": 8,
            "valid_required_points": 0,
            "avg_required_score": 0.0,
        },
        "validity": {
            "enough_keypoints": False,
            "reason": reason,
        },
    }


def _default_pushup_result(reason: str = "", selected: bool = False) -> Dict[str, Any]:
    return {
        "action_type": "pushup",
        "scoring_scope": "main_person_only",
        "main_person_selected": selected,
        "angles": {
            "left_elbow": 0.0,
            "right_elbow": 0.0,
            "elbow_angle": 0.0,
            "torso_lean": 0.0,
        },
        "alignment": {
            "body_line_deviation": 0.0,
            "hip_offset": 0.0,
            "hip_trend": "normal",
            "phase": "unknown",
        },
        "symmetry": {
            "elbow_diff": 0.0,
        },
        "confidence_summary": {
            "min_score_used": 0.0,
            "required_points": 10,
            "valid_required_points": 0,
            "avg_required_score": 0.0,
        },
        "validity": {
            "enough_keypoints": False,
            "reason": reason,
        },
    }


def _default_glute_bridge_result(reason: str = "", selected: bool = False) -> Dict[str, Any]:
    return {
        "action_type": "glute_bridge",
        "scoring_scope": "main_person_only",
        "main_person_selected": selected,
        "angles": {
            "left_hip": 0.0,
            "right_hip": 0.0,
            "hip_extension": 0.0,
            "left_knee": 0.0,
            "right_knee": 0.0,
            "knee_angle": 0.0,
        },
        "alignment": {
            "body_line_deviation": 0.0,
            "hip_offset": 0.0,
            "hip_trend": "normal",
            "phase": "unknown",
        },
        "symmetry": {
            "hip_diff": 0.0,
            "knee_diff": 0.0,
        },
        "confidence_summary": {
            "min_score_used": 0.0,
            "required_points": 8,
            "valid_required_points": 0,
            "avg_required_score": 0.0,
        },
        "validity": {
            "enough_keypoints": False,
            "reason": reason,
        },
    }


def _default_situp_result(reason: str = "", selected: bool = False) -> Dict[str, Any]:
    return {
        "action_type": "situp",
        "scoring_scope": "main_person_only",
        "main_person_selected": selected,
        "angles": {
            "left_hip": 0.0,
            "right_hip": 0.0,
            "hip_flexion": 0.0,
            "left_knee": 0.0,
            "right_knee": 0.0,
            "knee_angle": 0.0,
            "torso_angle": 0.0,
        },
        "alignment": {
            "torso_raise": 0.0,
            "phase": "unknown",
        },
        "symmetry": {
            "hip_diff": 0.0,
            "knee_diff": 0.0,
        },
        "confidence_summary": {
            "min_score_used": 0.0,
            "required_points": 8,
            "valid_required_points": 0,
            "avg_required_score": 0.0,
        },
        "validity": {
            "enough_keypoints": False,
            "reason": reason,
        },
    }


def _kp_valid(kp: Any, min_score: float) -> bool:
    if not isinstance(kp, (list, tuple)) or len(kp) < 3:
        return False
    x, y, s = kp[0], kp[1], kp[2]
    try:
        x = float(x)
        y = float(y)
        s = float(s)
    except Exception:
        return False
    if s < min_score:
        return False
    # Existing pipeline zeroes low-confidence kps into [0, 0, 0]
    if abs(x) < 1e-6 and abs(y) < 1e-6 and abs(s) < 1e-6:
        return False
    return True


def _point(kps: List[List[float]], idx: int, min_score: float) -> Optional[Tuple[float, float]]:
    if idx >= len(kps):
        return None
    kp = kps[idx]
    if not _kp_valid(kp, min_score):
        return None
    return float(kp[0]), float(kp[1])


def _score(kps: List[List[float]], idx: int, min_score: float) -> Optional[float]:
    if idx >= len(kps):
        return None
    kp = kps[idx]
    if not _kp_valid(kp, min_score):
        return None
    return float(kp[2])


def _angle_3pt(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> Optional[float]:
    # Angle ABC (at point B) in degrees, range [0, 180]
    bax = a[0] - b[0]
    bay = a[1] - b[1]
    bcx = c[0] - b[0]
    bcy = c[1] - b[1]
    n1 = math.hypot(bax, bay)
    n2 = math.hypot(bcx, bcy)
    if n1 < 1e-6 or n2 < 1e-6:
        return None
    cosv = (bax * bcx + bay * bcy) / (n1 * n2)
    cosv = max(-1.0, min(1.0, cosv))
    return math.degrees(math.acos(cosv))


def _torso_lean(shoulder_center: Tuple[float, float], hip_center: Tuple[float, float]) -> Optional[float]:
    # Angle between torso vector (hip -> shoulder) and vertical up direction (0, -1)
    vx = shoulder_center[0] - hip_center[0]
    vy = shoulder_center[1] - hip_center[1]
    n = math.hypot(vx, vy)
    if n < 1e-6:
        return None
    cosv = (-vy) / n  # dot((vx,vy),(0,-1)) / |v|
    cosv = max(-1.0, min(1.0, cosv))
    return math.degrees(math.acos(cosv))


def _bbox_area(person: Dict[str, Any]) -> float:
    bbox = person.get("bbox") or []
    if not isinstance(bbox, (list, tuple)) or len(bbox) < 4:
        return 0.0
    try:
        x1, y1, x2, y2 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
    except Exception:
        return 0.0
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def _pick_main_person(persons: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not persons:
        return None
    return max(persons, key=_bbox_area)


def _round_or_zero(v: Optional[float]) -> float:
    return round(float(v), 1) if v is not None else 0.0


def _angle_to_horizontal(a: Tuple[float, float], b: Tuple[float, float]) -> Optional[float]:
    # Absolute angle to horizontal in degrees, range [0, 90]
    vx = b[0] - a[0]
    vy = b[1] - a[1]
    n = math.hypot(vx, vy)
    if n < 1e-6:
        return None
    deg = abs(math.degrees(math.atan2(vy, vx)))
    if deg > 90:
        deg = 180 - deg
    return deg


def _project_point_on_line(
    a: Tuple[float, float],
    b: Tuple[float, float],
    p: Tuple[float, float],
) -> Optional[Tuple[float, float]]:
    abx = b[0] - a[0]
    aby = b[1] - a[1]
    ab2 = abx * abx + aby * aby
    if ab2 < 1e-6:
        return None
    apx = p[0] - a[0]
    apy = p[1] - a[1]
    t = (apx * abx + apy * aby) / ab2
    return a[0] + t * abx, a[1] + t * aby


def analyze_squat_from_persons(persons: List[Dict[str, Any]], min_score: Optional[float] = None) -> Dict[str, Any]:
    """
    Analyze squat posture from existing keypoint output.

    Input:
      persons: list of {"bbox": [...], "keypoints": [[x,y,score], ...]}
    Output:
      structured squat analysis dictionary.
    """
    if min_score is None:
        cfg_score = float(getattr(settings, "CONFIDENCE_THRESHOLD", 0.3)) if settings else 0.3
        # Slightly conservative floor to avoid unstable geometry
        min_score = max(0.2, cfg_score)

    if not persons:
        res = _default_result("未检测到人体", selected=False)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    person = _pick_main_person(persons)
    if not person:
        res = _default_result("未能选出主目标", selected=False)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    kps = person.get("keypoints") or []
    if not isinstance(kps, list) or not kps:
        res = _default_result("主目标缺少关键点数据", selected=True)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    required = {
        "left_shoulder": _point(kps, IDX_LEFT_SHOULDER, min_score),
        "right_shoulder": _point(kps, IDX_RIGHT_SHOULDER, min_score),
        "left_hip": _point(kps, IDX_LEFT_HIP, min_score),
        "right_hip": _point(kps, IDX_RIGHT_HIP, min_score),
        "left_knee": _point(kps, IDX_LEFT_KNEE, min_score),
        "right_knee": _point(kps, IDX_RIGHT_KNEE, min_score),
        "left_ankle": _point(kps, IDX_LEFT_ANKLE, min_score),
        "right_ankle": _point(kps, IDX_RIGHT_ANKLE, min_score),
    }
    required_indices = [
        IDX_LEFT_SHOULDER,
        IDX_RIGHT_SHOULDER,
        IDX_LEFT_HIP,
        IDX_RIGHT_HIP,
        IDX_LEFT_KNEE,
        IDX_RIGHT_KNEE,
        IDX_LEFT_ANKLE,
        IDX_RIGHT_ANKLE,
    ]
    required_scores = [s for s in (_score(kps, idx, min_score) for idx in required_indices) if s is not None]
    confidence_summary = {
        "min_score_used": round(float(min_score), 3),
        "required_points": len(required_indices),
        "valid_required_points": len(required_scores),
        "avg_required_score": round(sum(required_scores) / len(required_scores), 3) if required_scores else 0.0,
    }
    missing = [name for name, pt in required.items() if pt is None]
    if missing:
        res = _default_result(
            reason=f"关键点不足，缺失: {', '.join(missing)}",
            selected=True,
        )
        res["confidence_summary"] = confidence_summary
        return res

    left_shoulder = required["left_shoulder"]
    right_shoulder = required["right_shoulder"]
    left_hip = required["left_hip"]
    right_hip = required["right_hip"]
    left_knee = required["left_knee"]
    right_knee = required["right_knee"]
    left_ankle = required["left_ankle"]
    right_ankle = required["right_ankle"]

    shoulder_center = ((left_shoulder[0] + right_shoulder[0]) / 2.0, (left_shoulder[1] + right_shoulder[1]) / 2.0)
    hip_center = ((left_hip[0] + right_hip[0]) / 2.0, (left_hip[1] + right_hip[1]) / 2.0)

    left_knee_angle = _angle_3pt(left_hip, left_knee, left_ankle)
    right_knee_angle = _angle_3pt(right_hip, right_knee, right_ankle)
    left_hip_angle = _angle_3pt(left_shoulder, left_hip, left_knee)
    right_hip_angle = _angle_3pt(right_shoulder, right_hip, right_knee)
    torso_lean_angle = _torso_lean(shoulder_center, hip_center)

    if any(v is None for v in [left_knee_angle, right_knee_angle, left_hip_angle, right_hip_angle, torso_lean_angle]):
        res = _default_result("角度计算失败，关键点几何关系异常", selected=True)
        res["confidence_summary"] = confidence_summary
        return res

    knee_diff = abs(left_knee_angle - right_knee_angle)
    hip_diff = abs(left_hip_angle - right_hip_angle)

    return {
        "action_type": "squat",
        "scoring_scope": "main_person_only",
        "main_person_selected": True,
        "angles": {
            "left_knee": _round_or_zero(left_knee_angle),
            "right_knee": _round_or_zero(right_knee_angle),
            "left_hip": _round_or_zero(left_hip_angle),
            "right_hip": _round_or_zero(right_hip_angle),
            "torso_lean": _round_or_zero(torso_lean_angle),
        },
        "symmetry": {
            "knee_diff": _round_or_zero(knee_diff),
            "hip_diff": _round_or_zero(hip_diff),
        },
        "confidence_summary": confidence_summary,
        "validity": {
            "enough_keypoints": True,
            "reason": "",
        },
    }


def analyze_plank_from_persons(persons: List[Dict[str, Any]], min_score: Optional[float] = None) -> Dict[str, Any]:
    """
    Analyze plank posture (side-view MVP) from existing keypoint output.
    """
    if min_score is None:
        cfg_score = float(getattr(settings, "CONFIDENCE_THRESHOLD", 0.3)) if settings else 0.3
        min_score = max(0.2, cfg_score)

    if not persons:
        res = _default_plank_result("未检测到人体", selected=False)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    person = _pick_main_person(persons)
    if not person:
        res = _default_plank_result("未能选出主目标", selected=False)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    kps = person.get("keypoints") or []
    if not isinstance(kps, list) or not kps:
        res = _default_plank_result("主目标缺少关键点数据", selected=True)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    required_indices = [
        IDX_LEFT_SHOULDER,
        IDX_RIGHT_SHOULDER,
        IDX_LEFT_HIP,
        IDX_RIGHT_HIP,
        IDX_LEFT_KNEE,
        IDX_RIGHT_KNEE,
        IDX_LEFT_ANKLE,
        IDX_RIGHT_ANKLE,
    ]
    required_scores = [s for s in (_score(kps, idx, min_score) for idx in required_indices) if s is not None]
    confidence_summary = {
        "min_score_used": round(float(min_score), 3),
        "required_points": len(required_indices),
        "valid_required_points": len(required_scores),
        "avg_required_score": round(sum(required_scores) / len(required_scores), 3) if required_scores else 0.0,
    }

    left_shoulder = _point(kps, IDX_LEFT_SHOULDER, min_score)
    right_shoulder = _point(kps, IDX_RIGHT_SHOULDER, min_score)
    left_hip = _point(kps, IDX_LEFT_HIP, min_score)
    right_hip = _point(kps, IDX_RIGHT_HIP, min_score)
    left_ankle = _point(kps, IDX_LEFT_ANKLE, min_score)
    right_ankle = _point(kps, IDX_RIGHT_ANKLE, min_score)

    side_chains = []
    if left_shoulder and left_hip and left_ankle:
        side_chains.append(("left", left_shoulder, left_hip, left_ankle))
    if right_shoulder and right_hip and right_ankle:
        side_chains.append(("right", right_shoulder, right_hip, right_ankle))

    if not side_chains:
        res = _default_plank_result("关键点不足，至少需要一侧的肩-髋-踝关键点", selected=True)
        res["confidence_summary"] = confidence_summary
        return res

    hip_angles = []
    torso_leans = []
    line_deviations = []
    hip_offsets = []
    for _, shoulder, hip, ankle in side_chains:
        hip_angle = _angle_3pt(shoulder, hip, ankle)
        torso_lean = _angle_to_horizontal(shoulder, hip)
        proj = _project_point_on_line(shoulder, ankle, hip)
        body_len = math.hypot(ankle[0] - shoulder[0], ankle[1] - shoulder[1])
        if hip_angle is None or torso_lean is None or proj is None or body_len < 1e-6:
            continue
        # Normalize by body line length, unit: %
        delta_y_pct = ((hip[1] - proj[1]) / body_len) * 100.0
        hip_angles.append(hip_angle)
        torso_leans.append(torso_lean)
        line_deviations.append(abs(delta_y_pct))
        hip_offsets.append(delta_y_pct)

    if not hip_angles:
        res = _default_plank_result("角度计算失败，关键点几何关系异常", selected=True)
        res["confidence_summary"] = confidence_summary
        return res

    avg_hip_angle = sum(hip_angles) / len(hip_angles)
    avg_torso_lean = sum(torso_leans) / len(torso_leans)
    avg_deviation = sum(line_deviations) / len(line_deviations)
    avg_hip_offset = sum(hip_offsets) / len(hip_offsets)

    # image y-axis points downward:
    # positive offset => hip lower than shoulder-ankle line (hip_low)
    # negative offset => hip higher than shoulder-ankle line (hip_high)
    if avg_hip_offset > 4.0:
        hip_trend = "hip_low"
    elif avg_hip_offset < -4.0:
        hip_trend = "hip_high"
    else:
        hip_trend = "normal"

    reason = ""
    if len(side_chains) == 1:
        reason = "仅单侧关键点有效，可能为侧面遮挡，评分可靠性降低"

    return {
        "action_type": "plank",
        "scoring_scope": "main_person_only",
        "main_person_selected": True,
        "angles": {
            "hip_angle": _round_or_zero(avg_hip_angle),
            "torso_lean": _round_or_zero(avg_torso_lean),
        },
        "alignment": {
            "body_line_deviation": _round_or_zero(avg_deviation),
            "hip_offset": _round_or_zero(avg_hip_offset),
            "hip_trend": hip_trend,
        },
        "confidence_summary": confidence_summary,
        "validity": {
            "enough_keypoints": True,
            "reason": reason,
        },
    }


def analyze_pushup_from_persons(persons: List[Dict[str, Any]], min_score: Optional[float] = None) -> Dict[str, Any]:
    """
    Analyze push-up posture from existing keypoint output.
    Uses upper-limb elbow angle plus shoulder-hip-ankle alignment for a side/front-view MVP.
    """
    if min_score is None:
        cfg_score = float(getattr(settings, "CONFIDENCE_THRESHOLD", 0.3)) if settings else 0.3
        min_score = max(0.2, cfg_score)

    if not persons:
        res = _default_pushup_result("未检测到人体", selected=False)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    person = _pick_main_person(persons)
    if not person:
        res = _default_pushup_result("未能选出主目标", selected=False)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    kps = person.get("keypoints") or []
    if not isinstance(kps, list) or not kps:
        res = _default_pushup_result("主目标缺少关键点数据", selected=True)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    required_indices = [
        IDX_LEFT_SHOULDER,
        IDX_RIGHT_SHOULDER,
        IDX_LEFT_ELBOW,
        IDX_RIGHT_ELBOW,
        IDX_LEFT_WRIST,
        IDX_RIGHT_WRIST,
        IDX_LEFT_HIP,
        IDX_RIGHT_HIP,
        IDX_LEFT_ANKLE,
        IDX_RIGHT_ANKLE,
    ]
    required_scores = [s for s in (_score(kps, idx, min_score) for idx in required_indices) if s is not None]
    confidence_summary = {
        "min_score_used": round(float(min_score), 3),
        "required_points": len(required_indices),
        "valid_required_points": len(required_scores),
        "avg_required_score": round(sum(required_scores) / len(required_scores), 3) if required_scores else 0.0,
    }

    points = {
        "left_shoulder": _point(kps, IDX_LEFT_SHOULDER, min_score),
        "right_shoulder": _point(kps, IDX_RIGHT_SHOULDER, min_score),
        "left_elbow": _point(kps, IDX_LEFT_ELBOW, min_score),
        "right_elbow": _point(kps, IDX_RIGHT_ELBOW, min_score),
        "left_wrist": _point(kps, IDX_LEFT_WRIST, min_score),
        "right_wrist": _point(kps, IDX_RIGHT_WRIST, min_score),
        "left_hip": _point(kps, IDX_LEFT_HIP, min_score),
        "right_hip": _point(kps, IDX_RIGHT_HIP, min_score),
        "left_ankle": _point(kps, IDX_LEFT_ANKLE, min_score),
        "right_ankle": _point(kps, IDX_RIGHT_ANKLE, min_score),
    }

    side_chains = []
    if points["left_wrist"] and points["left_elbow"] and points["left_shoulder"] and points["left_hip"] and points["left_ankle"]:
        side_chains.append(("left", points["left_wrist"], points["left_elbow"], points["left_shoulder"], points["left_hip"], points["left_ankle"]))
    if points["right_wrist"] and points["right_elbow"] and points["right_shoulder"] and points["right_hip"] and points["right_ankle"]:
        side_chains.append(("right", points["right_wrist"], points["right_elbow"], points["right_shoulder"], points["right_hip"], points["right_ankle"]))

    if not side_chains:
        res = _default_pushup_result("关键点不足，至少需要一侧的腕-肘-肩-髋-踝关键点", selected=True)
        res["confidence_summary"] = confidence_summary
        return res

    elbow_by_side = {}
    torso_leans = []
    line_deviations = []
    hip_offsets = []
    for side, wrist, elbow, shoulder, hip, ankle in side_chains:
        elbow_angle = _angle_3pt(wrist, elbow, shoulder)
        torso_lean = _angle_to_horizontal(shoulder, hip)
        proj = _project_point_on_line(shoulder, ankle, hip)
        body_len = math.hypot(ankle[0] - shoulder[0], ankle[1] - shoulder[1])
        if elbow_angle is None or torso_lean is None or proj is None or body_len < 1e-6:
            continue
        delta_y_pct = ((hip[1] - proj[1]) / body_len) * 100.0
        elbow_by_side[side] = elbow_angle
        torso_leans.append(torso_lean)
        line_deviations.append(abs(delta_y_pct))
        hip_offsets.append(delta_y_pct)

    if not elbow_by_side:
        res = _default_pushup_result("角度计算失败，关键点几何关系异常", selected=True)
        res["confidence_summary"] = confidence_summary
        return res

    elbow_values = list(elbow_by_side.values())
    avg_elbow_angle = sum(elbow_values) / len(elbow_values)
    avg_torso_lean = sum(torso_leans) / len(torso_leans)
    avg_deviation = sum(line_deviations) / len(line_deviations)
    avg_hip_offset = sum(hip_offsets) / len(hip_offsets)
    elbow_diff = abs(elbow_by_side.get("left", avg_elbow_angle) - elbow_by_side.get("right", avg_elbow_angle))

    if avg_hip_offset > 4.0:
        hip_trend = "hip_low"
    elif avg_hip_offset < -4.0:
        hip_trend = "hip_high"
    else:
        hip_trend = "normal"

    if avg_elbow_angle <= 100.0:
        phase = "bottom"
    elif avg_elbow_angle >= 150.0:
        phase = "top"
    else:
        phase = "middle"

    reason = ""
    if len(side_chains) == 1:
        reason = "仅单侧关键点有效，评分可靠性降低"

    return {
        "action_type": "pushup",
        "scoring_scope": "main_person_only",
        "main_person_selected": True,
        "angles": {
            "left_elbow": _round_or_zero(elbow_by_side.get("left")),
            "right_elbow": _round_or_zero(elbow_by_side.get("right")),
            "elbow_angle": _round_or_zero(avg_elbow_angle),
            "torso_lean": _round_or_zero(avg_torso_lean),
        },
        "alignment": {
            "body_line_deviation": _round_or_zero(avg_deviation),
            "hip_offset": _round_or_zero(avg_hip_offset),
            "hip_trend": hip_trend,
            "phase": phase,
        },
        "symmetry": {
            "elbow_diff": _round_or_zero(elbow_diff),
        },
        "confidence_summary": confidence_summary,
        "validity": {
            "enough_keypoints": True,
            "reason": reason,
        },
    }


def analyze_glute_bridge_from_persons(persons: List[Dict[str, Any]], min_score: Optional[float] = None) -> Dict[str, Any]:
    """
    Analyze glute bridge posture from existing keypoint output.
    Uses shoulder-hip-knee alignment and knee flexion as a side/front-view MVP.
    """
    if min_score is None:
        cfg_score = float(getattr(settings, "CONFIDENCE_THRESHOLD", 0.3)) if settings else 0.3
        min_score = max(0.2, cfg_score)

    if not persons:
        res = _default_glute_bridge_result("未检测到人体", selected=False)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    person = _pick_main_person(persons)
    if not person:
        res = _default_glute_bridge_result("未能选出主目标", selected=False)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    kps = person.get("keypoints") or []
    if not isinstance(kps, list) or not kps:
        res = _default_glute_bridge_result("主目标缺少关键点数据", selected=True)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    required_indices = [
        IDX_LEFT_SHOULDER,
        IDX_RIGHT_SHOULDER,
        IDX_LEFT_HIP,
        IDX_RIGHT_HIP,
        IDX_LEFT_KNEE,
        IDX_RIGHT_KNEE,
        IDX_LEFT_ANKLE,
        IDX_RIGHT_ANKLE,
    ]
    required_scores = [s for s in (_score(kps, idx, min_score) for idx in required_indices) if s is not None]
    confidence_summary = {
        "min_score_used": round(float(min_score), 3),
        "required_points": len(required_indices),
        "valid_required_points": len(required_scores),
        "avg_required_score": round(sum(required_scores) / len(required_scores), 3) if required_scores else 0.0,
    }

    points = {
        "left_shoulder": _point(kps, IDX_LEFT_SHOULDER, min_score),
        "right_shoulder": _point(kps, IDX_RIGHT_SHOULDER, min_score),
        "left_hip": _point(kps, IDX_LEFT_HIP, min_score),
        "right_hip": _point(kps, IDX_RIGHT_HIP, min_score),
        "left_knee": _point(kps, IDX_LEFT_KNEE, min_score),
        "right_knee": _point(kps, IDX_RIGHT_KNEE, min_score),
        "left_ankle": _point(kps, IDX_LEFT_ANKLE, min_score),
        "right_ankle": _point(kps, IDX_RIGHT_ANKLE, min_score),
    }

    side_chains = []
    if points["left_shoulder"] and points["left_hip"] and points["left_knee"] and points["left_ankle"]:
        side_chains.append(("left", points["left_shoulder"], points["left_hip"], points["left_knee"], points["left_ankle"]))
    if points["right_shoulder"] and points["right_hip"] and points["right_knee"] and points["right_ankle"]:
        side_chains.append(("right", points["right_shoulder"], points["right_hip"], points["right_knee"], points["right_ankle"]))

    if not side_chains:
        res = _default_glute_bridge_result("关键点不足，至少需要一侧的肩-髋-膝-踝关键点", selected=True)
        res["confidence_summary"] = confidence_summary
        return res

    hip_by_side = {}
    knee_by_side = {}
    line_deviations = []
    hip_offsets = []
    for side, shoulder, hip, knee, ankle in side_chains:
        hip_angle = _angle_3pt(shoulder, hip, knee)
        knee_angle = _angle_3pt(hip, knee, ankle)
        proj = _project_point_on_line(shoulder, knee, hip)
        bridge_len = math.hypot(knee[0] - shoulder[0], knee[1] - shoulder[1])
        if hip_angle is None or knee_angle is None or proj is None or bridge_len < 1e-6:
            continue
        delta_y_pct = ((hip[1] - proj[1]) / bridge_len) * 100.0
        hip_by_side[side] = hip_angle
        knee_by_side[side] = knee_angle
        line_deviations.append(abs(delta_y_pct))
        hip_offsets.append(delta_y_pct)

    if not hip_by_side:
        res = _default_glute_bridge_result("角度计算失败，关键点几何关系异常", selected=True)
        res["confidence_summary"] = confidence_summary
        return res

    hip_values = list(hip_by_side.values())
    knee_values = list(knee_by_side.values())
    avg_hip_angle = sum(hip_values) / len(hip_values)
    avg_knee_angle = sum(knee_values) / len(knee_values)
    avg_deviation = sum(line_deviations) / len(line_deviations)
    avg_hip_offset = sum(hip_offsets) / len(hip_offsets)
    hip_diff = abs(hip_by_side.get("left", avg_hip_angle) - hip_by_side.get("right", avg_hip_angle))
    knee_diff = abs(knee_by_side.get("left", avg_knee_angle) - knee_by_side.get("right", avg_knee_angle))

    if avg_hip_offset > 4.0:
        hip_trend = "hip_low"
    elif avg_hip_offset < -4.0:
        hip_trend = "hip_high"
    else:
        hip_trend = "normal"

    if avg_hip_angle >= 165.0 and avg_deviation <= 6.0:
        phase = "top"
    elif avg_hip_angle >= 135.0:
        phase = "middle"
    else:
        phase = "bottom"

    reason = ""
    if len(side_chains) == 1:
        reason = "仅单侧关键点有效，评分可靠性降低"

    return {
        "action_type": "glute_bridge",
        "scoring_scope": "main_person_only",
        "main_person_selected": True,
        "angles": {
            "left_hip": _round_or_zero(hip_by_side.get("left")),
            "right_hip": _round_or_zero(hip_by_side.get("right")),
            "hip_extension": _round_or_zero(avg_hip_angle),
            "left_knee": _round_or_zero(knee_by_side.get("left")),
            "right_knee": _round_or_zero(knee_by_side.get("right")),
            "knee_angle": _round_or_zero(avg_knee_angle),
        },
        "alignment": {
            "body_line_deviation": _round_or_zero(avg_deviation),
            "hip_offset": _round_or_zero(avg_hip_offset),
            "hip_trend": hip_trend,
            "phase": phase,
        },
        "symmetry": {
            "hip_diff": _round_or_zero(hip_diff),
            "knee_diff": _round_or_zero(knee_diff),
        },
        "confidence_summary": confidence_summary,
        "validity": {
            "enough_keypoints": True,
            "reason": reason,
        },
    }


def analyze_situp_from_persons(persons: List[Dict[str, Any]], min_score: Optional[float] = None) -> Dict[str, Any]:
    """
    Analyze sit-up posture from existing keypoint output.
    Uses shoulder-hip-knee hip flexion and torso angle for a side/front-view MVP.
    """
    if min_score is None:
        cfg_score = float(getattr(settings, "CONFIDENCE_THRESHOLD", 0.3)) if settings else 0.3
        min_score = max(0.2, cfg_score)

    if not persons:
        res = _default_situp_result("未检测到人体", selected=False)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    person = _pick_main_person(persons)
    if not person:
        res = _default_situp_result("未能选出主目标", selected=False)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    kps = person.get("keypoints") or []
    if not isinstance(kps, list) or not kps:
        res = _default_situp_result("主目标缺少关键点数据", selected=True)
        res["confidence_summary"]["min_score_used"] = round(float(min_score), 3)
        return res

    required_indices = [
        IDX_LEFT_SHOULDER,
        IDX_RIGHT_SHOULDER,
        IDX_LEFT_HIP,
        IDX_RIGHT_HIP,
        IDX_LEFT_KNEE,
        IDX_RIGHT_KNEE,
        IDX_LEFT_ANKLE,
        IDX_RIGHT_ANKLE,
    ]
    required_scores = [s for s in (_score(kps, idx, min_score) for idx in required_indices) if s is not None]
    confidence_summary = {
        "min_score_used": round(float(min_score), 3),
        "required_points": len(required_indices),
        "valid_required_points": len(required_scores),
        "avg_required_score": round(sum(required_scores) / len(required_scores), 3) if required_scores else 0.0,
    }

    points = {
        "left_shoulder": _point(kps, IDX_LEFT_SHOULDER, min_score),
        "right_shoulder": _point(kps, IDX_RIGHT_SHOULDER, min_score),
        "left_hip": _point(kps, IDX_LEFT_HIP, min_score),
        "right_hip": _point(kps, IDX_RIGHT_HIP, min_score),
        "left_knee": _point(kps, IDX_LEFT_KNEE, min_score),
        "right_knee": _point(kps, IDX_RIGHT_KNEE, min_score),
        "left_ankle": _point(kps, IDX_LEFT_ANKLE, min_score),
        "right_ankle": _point(kps, IDX_RIGHT_ANKLE, min_score),
    }

    side_chains = []
    if points["left_shoulder"] and points["left_hip"] and points["left_knee"] and points["left_ankle"]:
        side_chains.append(("left", points["left_shoulder"], points["left_hip"], points["left_knee"], points["left_ankle"]))
    if points["right_shoulder"] and points["right_hip"] and points["right_knee"] and points["right_ankle"]:
        side_chains.append(("right", points["right_shoulder"], points["right_hip"], points["right_knee"], points["right_ankle"]))

    if not side_chains:
        res = _default_situp_result("关键点不足，至少需要一侧的肩-髋-膝-踝关键点", selected=True)
        res["confidence_summary"] = confidence_summary
        return res

    hip_by_side = {}
    knee_by_side = {}
    torso_angles = []
    for side, shoulder, hip, knee, ankle in side_chains:
        hip_angle = _angle_3pt(shoulder, hip, knee)
        knee_angle = _angle_3pt(hip, knee, ankle)
        torso_angle = _angle_to_horizontal(shoulder, hip)
        if hip_angle is None or knee_angle is None or torso_angle is None:
            continue
        hip_by_side[side] = hip_angle
        knee_by_side[side] = knee_angle
        torso_angles.append(torso_angle)

    if not hip_by_side:
        res = _default_situp_result("角度计算失败，关键点几何关系异常", selected=True)
        res["confidence_summary"] = confidence_summary
        return res

    hip_values = list(hip_by_side.values())
    knee_values = list(knee_by_side.values())
    avg_hip_angle = sum(hip_values) / len(hip_values)
    avg_knee_angle = sum(knee_values) / len(knee_values)
    avg_torso_angle = sum(torso_angles) / len(torso_angles)
    hip_diff = abs(hip_by_side.get("left", avg_hip_angle) - hip_by_side.get("right", avg_hip_angle))
    knee_diff = abs(knee_by_side.get("left", avg_knee_angle) - knee_by_side.get("right", avg_knee_angle))

    # Smaller shoulder-hip-knee angle means the trunk is closer to the thighs.
    torso_raise = max(0.0, min(100.0, (180.0 - avg_hip_angle) / 90.0 * 100.0))
    if avg_hip_angle <= 110.0:
        phase = "top"
    elif avg_hip_angle <= 145.0:
        phase = "middle"
    else:
        phase = "bottom"

    reason = ""
    if len(side_chains) == 1:
        reason = "仅单侧关键点有效，评分可靠性降低"

    return {
        "action_type": "situp",
        "scoring_scope": "main_person_only",
        "main_person_selected": True,
        "angles": {
            "left_hip": _round_or_zero(hip_by_side.get("left")),
            "right_hip": _round_or_zero(hip_by_side.get("right")),
            "hip_flexion": _round_or_zero(avg_hip_angle),
            "left_knee": _round_or_zero(knee_by_side.get("left")),
            "right_knee": _round_or_zero(knee_by_side.get("right")),
            "knee_angle": _round_or_zero(avg_knee_angle),
            "torso_angle": _round_or_zero(avg_torso_angle),
        },
        "alignment": {
            "torso_raise": _round_or_zero(torso_raise),
            "phase": phase,
        },
        "symmetry": {
            "hip_diff": _round_or_zero(hip_diff),
            "knee_diff": _round_or_zero(knee_diff),
        },
        "confidence_summary": confidence_summary,
        "validity": {
            "enough_keypoints": True,
            "reason": reason,
        },
    }
