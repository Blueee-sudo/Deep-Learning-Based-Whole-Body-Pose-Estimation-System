from django.urls import re_path

from .consumers import RealtimePoseConsumer

websocket_urlpatterns = [
    re_path(r"ws/pose/realtime/$", RealtimePoseConsumer.as_asgi()),
]
