from django.db import models


class Role(models.Model):
    role_id = models.SmallAutoField(primary_key=True)
    role_name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "role"


class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField(max_length=128, unique=True)
    password_hash = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.RESTRICT, db_column="role_id")
    avatar_url = models.CharField(max_length=512, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user"
        indexes = [
            models.Index(fields=["role"], name="idx_role_id"),
            models.Index(fields=["created_at"], name="idx_created_at"),
        ]


class DetectionHistory(models.Model):
    STATUS_CHOICES = [("pending", "pending"), ("processing", "processing"), ("done", "done"), ("failed", "failed")]
    INPUT_CHOICES = [("image", "image"), ("video", "video"), ("realtime", "realtime")]

    detection_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    input_type = models.CharField(max_length=16, choices=INPUT_CHOICES)
    original_filename = models.CharField(max_length=256, null=True, blank=True)
    file_path = models.CharField(max_length=512, null=True, blank=True)
    result_path = models.CharField(max_length=512, null=True, blank=True)
    person_count = models.SmallIntegerField(default=0)
    frame_count = models.BigIntegerField(default=0)
    inference_time_ms = models.FloatField(null=True, blank=True)
    model_name = models.CharField(max_length=64, default="RTMW-M-WholeBody")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    error_msg = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "detection_history"
        indexes = [
            models.Index(fields=["user", "created_at"], name="idx_user_created"),
            models.Index(fields=["status"], name="idx_status"),
            models.Index(fields=["input_type"], name="idx_input_type"),
            models.Index(fields=["created_at"], name="idx_dh_created_at"),
        ]


class PoseAnalysisResult(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    detection = models.OneToOneField(DetectionHistory, on_delete=models.CASCADE, db_column="detection_id")
    action_type = models.CharField(max_length=16)
    score = models.SmallIntegerField(null=True, blank=True)
    overall_comment = models.TextField(null=True, blank=True)
    metrics_json = models.JSONField(default=dict)
    analysis_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pose_analysis_result"
        indexes = [
            models.Index(fields=["action_type", "created_at"], name="idx_par_action_created"),
            models.Index(fields=["created_at"], name="idx_par_created_at"),
        ]


class KeypointData(models.Model):
    kp_id = models.BigAutoField(primary_key=True)
    detection = models.ForeignKey(DetectionHistory, on_delete=models.CASCADE, db_column="detection_id")
    person_index = models.SmallIntegerField(default=0)
    frame_index = models.BigIntegerField(default=0)
    keypoints = models.JSONField()
    bbox_x1 = models.FloatField(null=True, blank=True)
    bbox_y1 = models.FloatField(null=True, blank=True)
    bbox_x2 = models.FloatField(null=True, blank=True)
    bbox_y2 = models.FloatField(null=True, blank=True)
    bbox_score = models.FloatField(null=True, blank=True)
    avg_body_score = models.FloatField(null=True, blank=True)
    avg_face_score = models.FloatField(null=True, blank=True)
    avg_hand_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "keypoint_data"
        constraints = [
            models.UniqueConstraint(fields=["detection", "frame_index", "person_index"], name="uq_det_frame_person")
        ]
        indexes = [
            models.Index(fields=["detection", "frame_index"], name="idx_detection_frame"),
            models.Index(fields=["detection", "person_index"], name="idx_detection_person"),
        ]


class ModelMetrics(models.Model):
    metric_id = models.BigAutoField(primary_key=True)
    model_name = models.CharField(max_length=64)
    model_version = models.CharField(max_length=32, default="1.0")
    dataset_name = models.CharField(max_length=64, default="COCO-WholeBody")
    metric_type = models.CharField(max_length=32)
    keypoint_subset = models.CharField(max_length=32, default="wholebody")
    metric_value = models.FloatField()
    iou_threshold = models.FloatField(null=True, blank=True)
    eval_config = models.JSONField(null=True, blank=True)
    evaluated_at = models.DateField()
    notes = models.CharField(max_length=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "model_metrics"
        indexes = [
            models.Index(fields=["model_name", "model_version"], name="idx_model_version"),
            models.Index(fields=["metric_type"], name="idx_metric_type"),
            models.Index(fields=["evaluated_at"], name="idx_evaluated_at"),
        ]


class OperationLog(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, db_column="user_id")
    action = models.CharField(max_length=64)
    target_type = models.CharField(max_length=32, null=True, blank=True)
    target_id = models.BigIntegerField(null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    user_agent = models.CharField(max_length=256, null=True, blank=True)
    request_path = models.CharField(max_length=256, null=True, blank=True)
    request_method = models.CharField(max_length=8, null=True, blank=True)
    response_status = models.SmallIntegerField(null=True, blank=True)
    extra_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "operation_log"
        indexes = [
            models.Index(fields=["user", "action"], name="idx_user_action"),
            models.Index(fields=["created_at"], name="idx_log_created"),
            models.Index(fields=["action"], name="idx_log_action"),
            models.Index(fields=["target_type", "target_id"], name="idx_log_target"),
        ]
