from django.contrib import admin

from .models import DetectionHistory, KeypointData, ModelMetrics, OperationLog, Role, User

admin.site.register(Role)
admin.site.register(User)
admin.site.register(DetectionHistory)
admin.site.register(KeypointData)
admin.site.register(ModelMetrics)
admin.site.register(OperationLog)
