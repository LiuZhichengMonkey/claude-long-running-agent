"""
摄像头模块测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import cv2
    import numpy as np
    from src.camera import CameraCapture
except ImportError:
    cv2 = None


@unittest.skipIf(cv2 is None, "OpenCV not installed")
class TestCameraCapture(unittest.TestCase):
    """摄像头捕获测试"""

    def setUp(self):
        """测试前准备"""
        self.config_path = os.path.join(
            os.path.dirname(__file__), '..', 'config.json'
        )
        self.camera = CameraCapture(self.config_path)

    def tearDown(self):
        """测试后清理"""
        if self.camera:
            self.camera.close()

    def test_camera_creation(self):
        """测试摄像头对象创建"""
        self.assertIsNotNone(self.camera)
        self.assertFalse(self.camera.is_opened())

    def test_get_available_cameras(self):
        """测试获取可用摄像头"""
        cameras = self.camera.get_available_cameras(max_check=3)
        self.assertIsInstance(cameras, list)

    def test_config_loading(self):
        """测试配置加载"""
        config = self.camera.config
        self.assertIsInstance(config, dict)

    def test_camera_properties(self):
        """测试摄像头属性"""
        props = self.camera.get_properties()
        # 未打开时应该返回空字典
        self.assertEqual(props, {})


if __name__ == '__main__':
    unittest.main()
