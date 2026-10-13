import base64
import csv
import io
import os
import threading
import uuid
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from django.conf import settings
from django.db import IntegrityError, close_old_connections
from django.http import FileResponse, HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .auth_utils import create_access_token, get_current_user_from_header, hash_password, verify_password
from .models import DetectionHistory, KeypointData, ModelMetrics, OperationLog, PoseAnalysisResult, Role, User
from .serializers import DetectionSerializer, KeypointSerializer, ModelMetricsSerializer, OperationLogSerializer, UserSerializer
from .services.db_service import create_detection, save_keypoints, upsert_pose_analysis_result, write_op_log
from .services.inferencer import infer_image
from .services.llm_scoring import score_pose_with_doubao
from .services.pose_analysis import (
    analyze_glute_bridge_from_persons,
    analyze_plank_from_persons,
    analyze_pushup_from_persons,
    analyze_situp_from_persons,
    analyze_squat_from_persons,
)
from .services.visualizer import draw_pose

_VIDEO_PROGRESS = {}
SUPPORTED_ACTION_TYPES = {"squat", "plank", "pushup", "glute_bridge", "situp"}


def _decode_upload(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("无法解析图片")
    return img


def _encode_to_base64(image: np.ndarray, quality: int = 88) -> str:
    ok, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise ValueError("图片编码失败")
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()


def _require_user(request):
    user = get_current_user_from_header(request.headers.get("Authorization"))
    if not user:
        return None, JsonResponse({"detail": "未登录或 Token 无效"}, status=401)
    return user, None


def _require_admin(request):
    user, err = _require_user(request)
    if err:
        return None, err
    if user.role_id != 1:
        return None, JsonResponse({"detail": "需要管理员权限"}, status=403)
    return user, None


def _normal_user_role():
    return Role.objects.filter(role_id=2).first() or Role.objects.create(
        role_id=2,
        role_name="user",
        description="普通用户",
    )


def _get_normal_user_or_error(user_id: int):
    target = User.objects.filter(user_id=user_id).select_related("role").first()
    if not target:
        return None, JsonResponse({"detail": "用户不存在"}, status=404)
    if target.role_id == 1:
        return None, JsonResponse({"detail": "不能操作管理员账号"}, status=403)
    return target, None


def _safe_upload_name(name: str) -> str:
    base = os.path.basename(name or "")
    return base.replace("/", "_").replace("\\", "_") or "upload.jpg"


def _paginate(qs, page: int, size: int):
    total = qs.count()
    offset = (page - 1) * size
    return total, qs[offset: offset + size]


def _set_video_progress(detection_id: int, **kwargs):
    current = _VIDEO_PROGRESS.get(detection_id, {})
    current.update(kwargs)
    _VIDEO_PROGRESS[detection_id] = current


def _normalize_action_type(raw: str) -> str:
    action = str(raw or "").strip().lower()
    return action if action in SUPPORTED_ACTION_TYPES else "squat"


def _analyze_pose_by_action(persons, action_type: str):
    if action_type == "plank":
        return analyze_plank_from_persons(persons, min_score=0.2)
    if action_type == "pushup":
        return analyze_pushup_from_persons(persons, min_score=0.2)
    if action_type == "glute_bridge":
        return analyze_glute_bridge_from_persons(persons, min_score=0.2)
    if action_type == "situp":
        return analyze_situp_from_persons(persons, min_score=0.2)
    return analyze_squat_from_persons(persons, min_score=0.2)


def _process_video_detection(
    detection_id: int,
    input_path: str,
    output_path: str,
    frame_stride: int,
):
    close_old_connections()
    cap = None
    writer = None
    try:
        detection = DetectionHistory.objects.filter(detection_id=detection_id).first()
        if not detection:
            return

        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise ValueError("无法读取视频文件，请尝试转码为 H264 的 MP4")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

        _set_video_progress(
            detection_id,
            status="processing",
            total_frames=total_frames,
            processed_frames=0,
            inferred_frames=0,
            frame_stride=frame_stride,
        )

        frame_idx = 0
        inferred_frame_count = 0
        person_total = 0
        infer_total = 0.0
        last_persons = []
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            should_infer = frame_idx % frame_stride == 0 or not last_persons
            if should_infer:
                result = infer_image(frame)
                last_persons = result["persons"]
                save_keypoints(detection, last_persons, frame_index=frame_idx)
                person_total += len(last_persons)
                infer_total += result["inference_time_ms"]
                inferred_frame_count += 1

            vis = draw_pose(frame, last_persons)
            writer.write(vis)
            frame_idx += 1

            if frame_idx % 10 == 0:
                _set_video_progress(
                    detection_id,
                    status="processing",
                    total_frames=total_frames,
                    processed_frames=frame_idx,
                    inferred_frames=inferred_frame_count,
                    frame_stride=frame_stride,
                )
                DetectionHistory.objects.filter(detection_id=detection_id).update(frame_count=frame_idx)

        detection.status = "done"
        detection.result_path = str(output_path)
        detection.frame_count = frame_idx
        detection.person_count = int(person_total / inferred_frame_count) if inferred_frame_count else 0
        detection.inference_time_ms = round(infer_total, 2)
        detection.save()

        _set_video_progress(
            detection_id,
            status="done",
            total_frames=total_frames or frame_idx,
            processed_frames=frame_idx,
            inferred_frames=inferred_frame_count,
            frame_stride=frame_stride,
        )
    except Exception as e:
        DetectionHistory.objects.filter(detection_id=detection_id).update(status="failed", error_msg=str(e))
        _set_video_progress(
            detection_id,
            status="failed",
            error_msg=str(e),
        )
    finally:
        if cap is not None:
            cap.release()
        if writer is not None:
            writer.release()
        close_old_connections()


@api_view(["GET"])
def health(request):
    return JsonResponse({"status": "ok", "framework": "django"})


@api_view(["POST"])
@parser_classes([JSONParser])
def register(request):
    username = str(request.data.get("username", "")).strip()
    email = str(request.data.get("email", "")).strip()
    password = str(request.data.get("password", ""))
    if len(username) < 3 or len(password) < 8 or "@" not in email:
        return JsonResponse({"detail": "注册参数不合法"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"detail": "用户名已存在"}, status=409)
    if User.objects.filter(email=email).exists():
        return JsonResponse({"detail": "邮箱已被注册"}, status=409)

    role = Role.objects.filter(role_id=2).first() or Role.objects.create(role_id=2, role_name="user", description="普通用户")
    user = User.objects.create(username=username, email=email, password_hash=hash_password(password), role=role)
    write_op_log(action="register", user=user, request_path=request.path, request_method=request.method, response_status=201)
    return JsonResponse(UserSerializer(user).data, status=201)


@api_view(["POST"])
@parser_classes([JSONParser])
def login(request):
    username = str(request.data.get("username", "")).strip()
    password = str(request.data.get("password", ""))
    user = User.objects.filter(username=username).select_related("role").first()
    if not user or not verify_password(password, user.password_hash):
        write_op_log(action="login_fail", request_path=request.path, request_method=request.method, response_status=401)
        return JsonResponse({"detail": "用户名或密码错误"}, status=401)
    if not user.is_active:
        return JsonResponse({"detail": "账号已被禁用"}, status=403)

    user.last_login_at = timezone.now()
    user.save(update_fields=["last_login_at"])
    token = create_access_token(user.user_id, user.role_id)
    write_op_log(action="login", user=user, request_path=request.path, request_method=request.method, response_status=200)
    return JsonResponse(
        {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
            "user": UserSerializer(user).data,
        },
        status=200,
    )


@api_view(["GET", "PUT"])
@parser_classes([JSONParser])
def me(request):
    user, err = _require_user(request)
    if err:
        return err
    if request.method == "GET":
        return JsonResponse(UserSerializer(user).data)

    email = request.data.get("email")
    avatar_url = request.data.get("avatar_url")
    if email and email != user.email and User.objects.filter(email=email).exclude(user_id=user.user_id).exists():
        return JsonResponse({"detail": "邮箱已被其他账号使用"}, status=409)
    if email:
        user.email = email
    if avatar_url is not None:
        user.avatar_url = avatar_url
    user.save()
    return JsonResponse(UserSerializer(user).data)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def pose_image_infer(request):
    upload = request.FILES.get("file")
    if upload is None:
        return JsonResponse({"detail": "缺少 file 字段"}, status=400)
    if not str(upload.content_type).startswith("image/"):
        return JsonResponse({"detail": "仅支持图片文件"}, status=415)

    action_type = _normalize_action_type(request.data.get("action_type", "squat"))
    current_user = get_current_user_from_header(request.headers.get("Authorization"))
    detection = None
    input_path = None
    pose_analysis = _analyze_pose_by_action([], action_type)
    pose_score_result = {
        "score": None,
        "overall_comment": "评分服务暂时不可用",
        "problems": [],
        "suggestions": [],
    }
    try:
        file_bytes = upload.read()
        image = _decode_upload(file_bytes)
        media_dir = Path(settings.MEDIA_ROOT)
        input_dir = media_dir / "uploads"
        output_dir = media_dir / "results"
        if current_user:
            input_dir.mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)
            input_path = input_dir / f"{int(datetime.now().timestamp())}_{_safe_upload_name(upload.name)}"
            with open(input_path, "wb") as f:
                f.write(file_bytes)
        result = infer_image(image)
        pose_analysis = _analyze_pose_by_action(result.get("persons") or [], action_type)
        pose_score_result = score_pose_with_doubao(pose_analysis)
        annotated = draw_pose(image, result["persons"])
        result["annotated_image"] = _encode_to_base64(annotated)
        result["model_name"] = settings.MODEL_DISPLAY_NAME
        result["action_type"] = action_type
        if current_user:
            detection = create_detection(
                user=current_user,
                input_type="image",
                original_filename=upload.name,
                file_path=str(input_path) if input_path else None,
                model_name=settings.MODEL_DISPLAY_NAME,
            )
            result_path = output_dir / f"{detection.detection_id}_{uuid.uuid4().hex[:8]}.jpg"
            cv2.imwrite(str(result_path), annotated)
            save_keypoints(detection, result["persons"], frame_index=0)
            detection.status = "done"
            detection.result_path = str(result_path)
            detection.person_count = len(result["persons"])
            detection.frame_count = 1
            detection.inference_time_ms = result["inference_time_ms"]
            detection.save()
            try:
                upsert_pose_analysis_result(
                    detection=detection,
                    action_type=action_type,
                    pose_analysis=pose_analysis,
                    pose_score_result=pose_score_result,
                )
            except Exception:
                # Non-blocking for main inference flow.
                pass
        result["detection_id"] = detection.detection_id if detection else None
        result["download_url"] = f"/api/pose/image/{detection.detection_id}/result/" if detection else None
        result["pose_analysis"] = pose_analysis
        result["pose_score_result"] = pose_score_result
        return JsonResponse(result, status=200)
    except Exception as e:
        if detection:
            detection.status = "failed"
            detection.error_msg = str(e)
            detection.save()
        fail_analysis = dict(pose_analysis)
        validity = dict(fail_analysis.get("validity") or {})
        validity["enough_keypoints"] = False
        validity["reason"] = validity.get("reason") or "姿态估计失败，无法分析"
        fail_analysis["validity"] = validity
        return JsonResponse(
            {
                "detail": f"推理失败: {e}",
                "detection_id": detection.detection_id if detection else None,
                "persons": [],
                "annotated_image": None,
                "download_url": None,
                "model_name": settings.MODEL_DISPLAY_NAME,
                "pose_analysis": fail_analysis,
                "pose_score_result": {
                    "score": None,
                    "overall_comment": "评分服务暂时不可用",
                    "problems": [],
                    "suggestions": [],
                },
            },
            status=500,
        )


@api_view(["GET"])
def pose_image_result(request, detection_id: int):
    user, err = _require_user(request)
    if err:
        return err
    det = DetectionHistory.objects.filter(detection_id=detection_id, input_type="image").first()
    if not det:
        return JsonResponse({"detail": "记录不存在"}, status=404)
    if user.role_id != 1 and det.user_id != user.user_id:
        return JsonResponse({"detail": "无权访问此记录"}, status=403)
    if det.status != "done" or not det.result_path or not os.path.exists(det.result_path):
        return JsonResponse({"detail": "结果文件不存在"}, status=404)
    return FileResponse(open(det.result_path, "rb"), as_attachment=True, filename=f"pose_{det.detection_id}.jpg")


@api_view(["POST"])
@parser_classes([MultiPartParser])
def pose_video_infer(request):
    upload = request.FILES.get("file")
    if upload is None:
        return JsonResponse({"detail": "缺少 file 字段"}, status=400)

    current_user, err = _require_user(request)
    if err:
        return err

    media_dir = Path(settings.MEDIA_ROOT)
    input_dir = media_dir / "uploads"
    output_dir = media_dir / "results"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = input_dir / f"{int(datetime.now().timestamp())}_{_safe_upload_name(upload.name)}"
    with open(input_path, "wb") as f:
        for chunk in upload.chunks():
            f.write(chunk)

    default_stride = max(1, int(getattr(settings, "VIDEO_INFER_FRAME_STRIDE", 1)))
    raw_stride = request.data.get("frame_stride", default_stride)
    try:
        frame_stride = int(raw_stride)
    except (TypeError, ValueError):
        frame_stride = default_stride
    frame_stride = min(max(frame_stride, 1), 10)

    detection = create_detection(
        user=current_user,
        input_type="video",
        original_filename=upload.name,
        file_path=str(input_path),
        model_name=settings.MODEL_DISPLAY_NAME,
    )
    detection.status = "processing"
    detection.save(update_fields=["status"])

    output_path = output_dir / f"{detection.detection_id}_result.mp4"
    _set_video_progress(
        detection.detection_id,
        status="processing",
        total_frames=0,
        processed_frames=0,
        inferred_frames=0,
        frame_stride=frame_stride,
    )
    worker = threading.Thread(
        target=_process_video_detection,
        args=(detection.detection_id, str(input_path), str(output_path), frame_stride),
        daemon=True,
    )
    worker.start()
    return JsonResponse(
        {
            "detection_id": detection.detection_id,
            "status": "processing",
            "frame_stride": frame_stride,
            "total_frames": 0,
            "inferred_frames": 0,
            "download_url": f"/api/pose/video/{detection.detection_id}/result/",
        }
    )


@api_view(["GET"])
def pose_video_progress(request, detection_id: int):
    user, err = _require_user(request)
    if err:
        return err
    det = DetectionHistory.objects.filter(detection_id=detection_id).first()
    if not det:
        return JsonResponse({"detail": "记录不存在"}, status=404)
    if user.role_id != 1 and det.user_id != user.user_id:
        return JsonResponse({"detail": "无权访问此记录"}, status=403)

    progress = _VIDEO_PROGRESS.get(detection_id, {})
    status_value = progress.get("status", det.status)
    total_frames = int(progress.get("total_frames") or 0)
    processed_frames = int(progress.get("processed_frames") or det.frame_count or 0)
    inferred_frames = int(progress.get("inferred_frames") or 0)
    frame_stride = int(progress.get("frame_stride") or getattr(settings, "VIDEO_INFER_FRAME_STRIDE", 1))
    if status_value == "done" and total_frames == 0:
        total_frames = int(det.frame_count or 0)
    percent = int((processed_frames * 100 / total_frames)) if total_frames > 0 else 0
    if status_value == "done":
        percent = 100
    elif status_value == "processing" and total_frames == 0:
        percent = 0

    return JsonResponse(
        {
            "detection_id": det.detection_id,
            "status": status_value,
            "total_frames": total_frames,
            "processed_frames": processed_frames,
            "inferred_frames": inferred_frames,
            "frame_stride": frame_stride,
            "progress_percent": max(0, min(percent, 100)),
            "error_msg": progress.get("error_msg") or det.error_msg,
            "download_url": f"/api/pose/video/{det.detection_id}/result/" if status_value == "done" else None,
        }
    )


@api_view(["GET"])
def pose_video_result(request, detection_id: int):
    user, err = _require_user(request)
    if err:
        return err
    det = DetectionHistory.objects.filter(detection_id=detection_id).first()
    if not det:
        return JsonResponse({"detail": "记录不存在"}, status=404)
    if user.role_id != 1 and det.user_id != user.user_id:
        return JsonResponse({"detail": "无权访问此记录"}, status=403)
    if det.status != "done" or not det.result_path or not os.path.exists(det.result_path):
        return JsonResponse({"detail": "结果文件不存在"}, status=404)
    return FileResponse(open(det.result_path, "rb"), as_attachment=True, filename=f"pose_{det.detection_id}.mp4")


@api_view(["POST"])
@parser_classes([JSONParser])
def realtime_frame_infer(request):
    b64 = request.data.get("frame")
    if not b64:
        return JsonResponse({"detail": "缺少 frame 字段"}, status=400)
    try:
        img_bytes = base64.b64decode(b64)
        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        result = infer_image(frame)
        return JsonResponse(result, status=200)
    except Exception as e:
        return JsonResponse({"detail": f"实时帧推理失败: {e}"}, status=500)


@api_view(["GET"])
def history_list(request):
    user, err = _require_user(request)
    if err:
        return err
    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("size", 20))
    input_type = request.GET.get("input_type")
    status = request.GET.get("status")
    start_time = request.GET.get("start_time")
    end_time = request.GET.get("end_time")

    qs = DetectionHistory.objects.filter(user_id=user.user_id).order_by("-created_at")
    if input_type:
        qs = qs.filter(input_type=input_type)
    if status:
        qs = qs.filter(status=status)
    if start_time:
        qs = qs.filter(created_at__gte=start_time)
    if end_time:
        qs = qs.filter(created_at__lte=end_time)
    total, items = _paginate(qs, page, size)
    return JsonResponse({"total": total, "page": page, "size": size, "items": DetectionSerializer(items, many=True).data})


@api_view(["GET"])
def history_detail(request, detection_id: int):
    user, err = _require_user(request)
    if err:
        return err
    with_keypoints = request.GET.get("with_keypoints", "false").lower() == "true"
    frame_index = request.GET.get("frame_index")

    det = DetectionHistory.objects.filter(detection_id=detection_id).first()
    if not det:
        return JsonResponse({"detail": "记录不存在"}, status=404)
    if user.role_id != 1 and det.user_id != user.user_id:
        return JsonResponse({"detail": "无权访问此记录"}, status=403)

    data = DetectionSerializer(det).data
    if with_keypoints:
        kqs = KeypointData.objects.filter(detection_id=detection_id).order_by("frame_index", "person_index")
        if frame_index is not None:
            kqs = kqs.filter(frame_index=int(frame_index))
        data["keypoints"] = KeypointSerializer(kqs, many=True).data
    return JsonResponse(data)


@api_view(["DELETE"])
def history_delete(request, detection_id: int):
    user, err = _require_user(request)
    if err:
        return err
    det = DetectionHistory.objects.filter(detection_id=detection_id).first()
    if not det:
        return JsonResponse({"detail": "记录不存在"}, status=404)
    if user.role_id != 1 and det.user_id != user.user_id:
        return JsonResponse({"detail": "无权访问此记录"}, status=403)
    det.delete()
    return HttpResponse(status=204)


@api_view(["GET"])
def history_export(request):
    user, err = _require_user(request)
    if err:
        return err
    fmt = request.GET.get("fmt", "csv").lower()
    input_type = request.GET.get("input_type")
    status = request.GET.get("status") or "done"
    qs = DetectionHistory.objects.filter(user_id=user.user_id).order_by("-created_at")
    if input_type:
        qs = qs.filter(input_type=input_type)
    if status:
        qs = qs.filter(status=status)
    qs = qs[:10000]
    rows = []
    for det in qs:
        kp = KeypointData.objects.filter(detection_id=det.detection_id, frame_index=0).first()
        rows.append(
            {
                "检测ID": det.detection_id,
                "输入类型": det.input_type,
                "文件名": det.original_filename or "",
                "检测人数": det.person_count,
                "帧数": det.frame_count,
                "推理耗时(ms)": round(det.inference_time_ms or 0, 1),
                "状态": det.status,
                "创建时间": det.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "身体置信度": round(kp.avg_body_score, 3) if kp and kp.avg_body_score else "",
                "脸部置信度": round(kp.avg_face_score, 3) if kp and kp.avg_face_score else "",
                "手部置信度": round(kp.avg_hand_score, 3) if kp and kp.avg_hand_score else "",
            }
        )
    headers = list(rows[0].keys()) if rows else ["检测ID", "输入类型", "文件名", "检测人数", "帧数", "推理耗时(ms)", "状态", "创建时间"]
    if fmt == "excel":
        try:
            import openpyxl
        except Exception:
            return JsonResponse({"detail": "请安装 openpyxl"}, status=500)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(headers)
        for row in rows:
            ws.append([row.get(h, "") for h in headers])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        resp = HttpResponse(
            buf.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="history_{user.user_id}.xlsx"'
        return resp

    sio = io.StringIO()
    sio.write("\ufeff")
    writer = csv.DictWriter(sio, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
    resp = HttpResponse(sio.getvalue(), content_type="text/csv; charset=utf-8-sig")
    resp["Content-Disposition"] = f'attachment; filename="history_{user.user_id}.csv"'
    return resp


@api_view(["GET"])
def pose_history_list(request):
    user, err = _require_user(request)
    if err:
        return err

    action_type = str(request.GET.get("action_type", "")).strip().lower()
    if action_type and action_type not in SUPPORTED_ACTION_TYPES:
        return JsonResponse({"detail": "action_type 仅支持 squat、plank、pushup、glute_bridge 或 situp"}, status=400)

    qs = (
        PoseAnalysisResult.objects.select_related("detection")
        .filter(detection__user_id=user.user_id, detection__input_type="image")
        .order_by("-created_at")
    )
    if action_type:
        qs = qs.filter(action_type=action_type)

    # Minimal viable history API: no paging by default, optional light limit.
    limit = int(request.GET.get("limit", 200))
    limit = max(1, min(limit, 1000))
    items = [
        {
            "detection_id": item.detection_id,
            "action_type": item.action_type,
            "score": item.score,
            "overall_comment": item.overall_comment,
            "metrics_json": item.metrics_json or {},
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for item in qs[:limit]
    ]
    return JsonResponse({"items": items, "total": len(items)})


@api_view(["GET", "POST"])
@parser_classes([JSONParser])
def admin_users(request):
    admin, err = _require_admin(request)
    if err:
        return err
    if request.method == "POST":
        username = str(request.data.get("username", "")).strip()
        email = str(request.data.get("email", "")).strip()
        password = str(request.data.get("password", ""))
        avatar_url = request.data.get("avatar_url", "")
        is_active = bool(request.data.get("is_active", True))
        if len(username) < 3 or len(password) < 8 or "@" not in email:
            return JsonResponse({"detail": "用户参数不合法，用户名至少 3 位，密码至少 8 位，邮箱需合法"}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({"detail": "用户名已存在"}, status=409)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"detail": "邮箱已被注册"}, status=409)
        try:
            user = User.objects.create(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role=_normal_user_role(),
                avatar_url=avatar_url,
                is_active=is_active,
            )
        except IntegrityError:
            return JsonResponse({"detail": "用户创建失败，请检查用户名或邮箱是否重复"}, status=409)
        write_op_log(
            action="admin_create_user",
            user=admin,
            request_path=request.path,
            request_method=request.method,
            response_status=201,
            extra_data={"target_user_id": user.user_id},
        )
        return JsonResponse(UserSerializer(user).data, status=201)

    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("size", 20))
    role_id = request.GET.get("role_id")
    qs = User.objects.select_related("role").order_by("-created_at")
    if role_id:
        qs = qs.filter(role_id=int(role_id))
    total, items = _paginate(qs, page, size)
    return JsonResponse({"total": total, "page": page, "size": size, "items": UserSerializer(items, many=True).data})


@api_view(["GET", "PUT", "DELETE"])
@parser_classes([JSONParser])
def admin_user_detail(request, user_id: int):
    admin, err = _require_admin(request)
    if err:
        return err
    target, err = _get_normal_user_or_error(user_id)
    if err:
        return err

    if request.method == "GET":
        return JsonResponse(UserSerializer(target).data)

    if request.method == "DELETE":
        target_id = target.user_id
        target.delete()
        write_op_log(
            action="admin_delete_user",
            user=admin,
            request_path=request.path,
            request_method=request.method,
            response_status=200,
            extra_data={"target_user_id": target_id},
        )
        return JsonResponse({"detail": "删除成功"})

    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    avatar_url = request.data.get("avatar_url")
    is_active = request.data.get("is_active")

    if username is not None:
        username = str(username).strip()
        if len(username) < 3:
            return JsonResponse({"detail": "用户名至少 3 位"}, status=400)
        if User.objects.filter(username=username).exclude(user_id=target.user_id).exists():
            return JsonResponse({"detail": "用户名已存在"}, status=409)
        target.username = username
    if email is not None:
        email = str(email).strip()
        if "@" not in email:
            return JsonResponse({"detail": "邮箱格式不合法"}, status=400)
        if User.objects.filter(email=email).exclude(user_id=target.user_id).exists():
            return JsonResponse({"detail": "邮箱已被其他账号使用"}, status=409)
        target.email = email
    if password:
        password = str(password)
        if len(password) < 8:
            return JsonResponse({"detail": "密码至少 8 位"}, status=400)
        target.password_hash = hash_password(password)
    if avatar_url is not None:
        target.avatar_url = avatar_url
    if is_active is not None:
        target.is_active = bool(is_active)
    target.role = _normal_user_role()
    target.save()
    write_op_log(
        action="admin_update_user",
        user=admin,
        request_path=request.path,
        request_method=request.method,
        response_status=200,
        extra_data={"target_user_id": target.user_id},
    )
    return JsonResponse(UserSerializer(target).data)


@api_view(["GET"])
def admin_detections(request):
    _, err = _require_admin(request)
    if err:
        return err
    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("size", 20))
    user_id = request.GET.get("user_id")
    qs = DetectionHistory.objects.order_by("-created_at")
    if user_id:
        qs = qs.filter(user_id=int(user_id))
    total, items = _paginate(qs, page, size)
    return JsonResponse({"total": total, "page": page, "size": size, "items": DetectionSerializer(items, many=True).data})


@api_view(["GET"])
def admin_logs(request):
    _, err = _require_admin(request)
    if err:
        return err
    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("size", 50))
    user_id = request.GET.get("user_id")
    action = request.GET.get("action")
    qs = OperationLog.objects.order_by("-created_at")
    if user_id:
        qs = qs.filter(user_id=int(user_id))
    if action:
        qs = qs.filter(action=action)
    total, items = _paginate(qs, page, size)
    return JsonResponse({"total": total, "page": page, "size": size, "items": OperationLogSerializer(items, many=True).data})


@api_view(["GET", "POST"])
@parser_classes([JSONParser])
def admin_metrics(request):
    _, err = _require_admin(request)
    if err:
        return err
    if request.method == "GET":
        model_name = request.GET.get("model_name")
        metric_type = request.GET.get("metric_type")
        keypoint_subset = request.GET.get("keypoint_subset")
        qs = ModelMetrics.objects.order_by("-evaluated_at")
        if model_name:
            qs = qs.filter(model_name=model_name)
        if metric_type:
            qs = qs.filter(metric_type=metric_type)
        if keypoint_subset:
            qs = qs.filter(keypoint_subset=keypoint_subset)
        return JsonResponse(ModelMetricsSerializer(qs, many=True).data, safe=False)

    payload = dict(request.data)
    serializer = ModelMetricsSerializer(data=payload)
    if not serializer.is_valid():
        return JsonResponse({"detail": serializer.errors}, status=400)
    item = serializer.save()
    return JsonResponse(ModelMetricsSerializer(item).data, status=201)


@api_view(["GET"])
def admin_metrics_plot(request):
    _, err = _require_admin(request)
    if err:
        return err

    model_name = request.GET.get("model_name")
    metric_type = request.GET.get("metric_type")
    keypoint_subset = request.GET.get("keypoint_subset")
    qs = ModelMetrics.objects.order_by("evaluated_at", "metric_id")
    if model_name:
        qs = qs.filter(model_name=model_name)
    if metric_type:
        qs = qs.filter(metric_type=metric_type)
    if keypoint_subset:
        qs = qs.filter(keypoint_subset=keypoint_subset)
    items = list(qs[:300])
    if not items:
        return JsonResponse({"detail": "暂无指标数据"}, status=404)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid")
    labels = [i.evaluated_at.strftime("%Y-%m-%d") for i in items]
    values = [i.metric_value for i in items]
    x = list(range(len(items)))

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(x=x, y=values, marker="o", color="#409EFF", ax=ax)
    title = f"{metric_type or 'metric'} trend ({keypoint_subset or 'all'})"
    ax.set_title(title)
    ax.set_xlabel("evaluation")
    ax.set_ylabel("value")
    step = max(1, len(labels) // 12)
    ax.set_xticks(x[::step])
    ax.set_xticklabels(labels[::step], rotation=35, ha="right")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140)
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type="image/png")
