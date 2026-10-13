from rest_framework import serializers

from .models import DetectionHistory, KeypointData, ModelMetrics, OperationLog, Role, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["role_id", "role_name", "description", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email",
            "role",
            "role_id",
            "avatar_url",
            "is_active",
            "last_login_at",
            "created_at",
            "updated_at",
        ]


class DetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionHistory
        fields = "__all__"


class KeypointSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeypointData
        fields = "__all__"


class ModelMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelMetrics
        fields = "__all__"


class OperationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationLog
        fields = "__all__"
