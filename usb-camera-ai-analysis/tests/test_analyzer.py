"""
AI分析模块测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import cv2
    import numpy as np
    from src.analyzer import ImageAnalyzer
except ImportError:
    cv2 = None


@unittest.skipIf(cv2 is None, "OpenCV not installed")
class TestImageAnalyzer(unittest.TestCase):
    """图像分析器测试"""

    def setUp(self):
        """测试前准备"""
        self.config_path = os.path.join(
            os.path.dirname(__file__), '..', 'config.json'
        )
        self.analyzer = ImageAnalyzer(self.config_path)
        # 创建测试图像
        self.test_image = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_analyzer_creation(self):
        """测试分析器对象创建"""
        self.assertIsNotNone(self.analyzer)

    def test_config_loading(self):
        """测试配置加载"""
        config = self.analyzer.config
        self.assertIsInstance(config, dict)

    def test_analyze_empty_image(self):
        """测试空图像分析"""
        results = self.analyzer.analyze(self.test_image)
        self.assertIsInstance(results, dict)
        self.assertIn('ocr', results)
        self.assertIn('ui_detection', results)
        self.assertIn('anomaly_detection', results)

    def test_detect_anomalies(self):
        """测试异常检测"""
        results = self.analyzer.detect_anomalies(self.test_image)
        self.assertIsInstance(results, dict)
        self.assertIn('colors', results)

    def test_compare_images(self):
        """测试图像对比"""
        image1 = np.zeros((480, 640, 3), dtype=np.uint8)
        image2 = np.ones((480, 640, 3), dtype=np.uint8) * 255

        results = self.analyzer.compare_images(image1, image2)
        self.assertIsInstance(results, dict)
        self.assertIn('diff_pixels', results)
        self.assertIn('diff_percentage', results)
        self.assertTrue(results['is_different'])

    def test_image_to_base64(self):
        """测试图像转base64"""
        b64 = self.analyzer.image_to_base64(self.test_image)
        self.assertIsInstance(b64, str)
        self.assertTrue(len(b64) > 0)

    def test_draw_ocr_results(self):
        """测试绘制OCR结果"""
        ocr_results = [
            {
                'text': 'Test',
                'confidence': 0.9,
                'box': [[10, 10], [50, 10], [50, 30], [10, 30]]
            }
        ]
        result = self.analyzer.draw_ocr_results(self.test_image, ocr_results)
        self.assertEqual(result.shape, self.test_image.shape)

    def test_draw_ui_results(self):
        """测试绘制UI检测结果"""
        ui_results = [
            {
                'class': 'button',
                'confidence': 0.9,
                'bbox': [10, 10, 50, 30]
            }
        ]
        result = self.analyzer.draw_ui_results(self.test_image, ui_results)
        self.assertEqual(result.shape, self.test_image.shape)


if __name__ == '__main__':
    unittest.main()
