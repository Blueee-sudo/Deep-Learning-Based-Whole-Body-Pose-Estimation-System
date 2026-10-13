import base64
import json
import logging

import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer

from .services.inferencer import infer_image

logger = logging.getLogger(__name__)


class RealtimePoseConsumer(AsyncWebsocketConsumer):
    """
    客户端发送:
      {"frame": "<base64_jpeg>"}
    服务端返回:
      {"persons":[...], "inference_time_ms": 12.3, "frame_idx": 3, "image_size": {...}}
    """

    async def connect(self):
        await self.accept()
        self.frame_idx = 0
        await self.send(text_data=json.dumps({"message": "connected"}))

    async def disconnect(self, close_code):
        logger.info("WebSocket disconnected: %s", close_code)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            await self.send(text_data=json.dumps({"error": "empty message"}))
            return
        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "invalid json"}))
            return

        frame_b64 = payload.get("frame")
        if not frame_b64:
            await self.send(text_data=json.dumps({"error": "missing frame field"}))
            return
        try:
            img_bytes = base64.b64decode(frame_b64)
            arr = np.frombuffer(img_bytes, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is None:
                raise ValueError("decode failed")
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"frame decode error: {e}"}))
            return

        try:
            result = infer_image(frame)
            result["frame_idx"] = self.frame_idx
            self.frame_idx += 1
            await self.send(text_data=json.dumps(result))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"infer failed: {e}"}))
