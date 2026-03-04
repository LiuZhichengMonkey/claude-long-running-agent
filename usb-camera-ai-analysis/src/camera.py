"""
摄像头捕获模块
支持USB摄像头捕获、配置和管理
"""

import cv2
import numpy as np
import json
import os
from typing import Optional, Dict, Any, Tuple, Generator
import threading
import time


class CameraCapture:
    """USB摄像头捕获类"""

    def __init__(self, config_path: str = "config.json"):
        """初始化摄像头捕获

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.camera_config = self.config.get("camera", {})

        self.device_index = self.camera_config.get("device_index", 0)
        self.resolution = self.camera_config.get("resolution", {"width": 1280, "height": 720})
        self.fps = self.camera_config.get("fps", 30)
        self.auto_exposure = self.camera_config.get("auto_exposure", True)

        self._cap: Optional[cv2.VideoCapture] = None
        self._is_opened = False
        self._lock = threading.Lock()
        self._current_frame = None

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def open(self) -> bool:
        """打开摄像头

        Returns:
            是否成功打开
        """
        with self._lock:
            if self._is_opened:
                return True

            self._cap = cv2.VideoCapture(self.device_index)

            if not self._cap.isOpened():
                self._cap.release()
                self._cap = None
                return False

            # 设置分辨率
            width = self.resolution.get("width", 1280)
            height = self.resolution.get("height", 720)
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self._cap.set(cv2.CAP_PROP_FPS, self.fps)

            # 设置自动曝光
            if self.auto_exposure:
                self._cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)  # 0.75 = auto
            else:
                self._cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25 = manual

            self._is_opened = True
            return True

    def close(self) -> None:
        """关闭摄像头"""
        with self._lock:
            if self._cap is not None:
                self._cap.release()
                self._cap = None
            self._is_opened = False

    def is_opened(self) -> bool:
        """检查摄像头是否打开"""
        return self._is_opened and self._cap is not None and self._cap.isOpened()

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """读取下一帧

        Returns:
            (是否成功, 帧图像)
        """
        with self._lock:
            if not self.is_opened():
                return False, None

            ret, frame = self._cap.read()
            if ret:
                self._current_frame = frame
            return ret, frame

    def get_frame(self) -> Optional[np.ndarray]:
        """获取当前帧"""
        with self._lock:
            return self._current_frame

    def stream(self) -> Generator[np.ndarray, None, None]:
        """视频流生成器

        Yields:
            帧图像
        """
        while self.is_opened():
            ret, frame = self.read()
            if ret:
                yield frame
            else:
                break

    def capture_image(self, filepath: str) -> bool:
        """保存当前帧到文件

        Args:
            filepath: 保存路径

        Returns:
            是否成功
        """
        frame = self.get_frame()
        if frame is None:
            return False

        # 确保目录存在
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)

        success = cv2.imwrite(filepath, frame)
        return success

    def get_available_cameras(self, max_check: int = 5) -> list:
        """检测可用摄像头

        Args:
            max_check: 最大检测数量

        Returns:
            可用摄像头索引列表
        """
        available = []
        for i in range(max_check):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available

    def get_properties(self) -> Dict[str, Any]:
        """获取摄像头属性

        Returns:
            摄像头属性字典
        """
        if not self.is_opened():
            return {}

        with self._lock:
            return {
                "width": int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": int(self._cap.get(cv2.CAP_PROP_FPS)),
                "brightness": self._cap.get(cv2.CAP_PROP_BRIGHTNESS),
                "contrast": self._cap.get(cv2.CAP_PROP_CONTRAST),
                "saturation": self._cap.get(cv2.CAP_PROP_SATURATION),
                "auto_exposure": self._cap.get(cv2.CAP_PROP_AUTO_EXPOSURE),
            }

    def set_property(self, prop_id: int, value: float) -> bool:
        """设置摄像头属性

        Args:
            prop_id: OpenCV属性ID
            value: 属性值

        Returns:
            是否成功
        """
        if not self.is_opened():
            return False

        with self._lock:
            return self._cap.set(prop_id, value)

    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


def create_camera(config_path: str = "config.json") -> CameraCapture:
    """创建摄像头捕获实例

    Args:
        config_path: 配置文件路径

    Returns:
        CameraCapture实例
    """
    return CameraCapture(config_path)
