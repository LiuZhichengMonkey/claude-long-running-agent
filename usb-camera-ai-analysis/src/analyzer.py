"""
AI分析模块
包含OCR、UI元素检测、异常检测等功能
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, Any, List, Optional, Tuple
import base64
from io import BytesIO


class ImageAnalyzer:
    """图像AI分析类"""

    def __init__(self, config_path: str = "config.json"):
        """初始化分析器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)

        # OCR配置
        self.ocr_config = self.config.get("ocr", {})
        self.ocr_enabled = self.ocr_config.get("enabled", True)
        self._ocr_model = None

        # UI检测配置
        self.ui_config = self.config.get("ui_detection", {})
        self.ui_enabled = self.ui_config.get("enabled", True)
        self._ui_model = None

        # 异常检测配置
        self.anomaly_config = self.config.get("anomaly_detection", {})
        self.anomaly_enabled = self.anomaly_config.get("enabled", True)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _init_ocr(self):
        """初始化OCR模型"""
        if self._ocr_model is not None:
            return

        try:
            from paddleocr import PaddleOCR

            lang = self.ocr_config.get("lang", "ch,en")
            use_angle_cls = self.ocr_config.get("use_angle_cls", True)

            self._ocr_model = PaddleOCR(
                use_angle_cls=use_angle_cls,
                lang=lang,
                show_log=False
            )
        except ImportError:
            print("PaddleOCR not installed, OCR disabled")
            self.ocr_enabled = False
        except Exception as e:
            print(f"Failed to initialize OCR: {e}")
            self.ocr_enabled = False

    def _init_ui_detection(self):
        """初始化UI检测模型"""
        if self._ui_model is not None:
            return

        try:
            from ultralytics import YOLO

            model_path = self.ui_config.get("model_path", "yolov8n.pt")
            self._ui_model = YOLO(model_path)
        except ImportError:
            print("Ultralytics not installed, UI detection disabled")
            self.ui_enabled = False
        except Exception as e:
            print(f"Failed to initialize UI detection: {e}")
            self.ui_enabled = False

    def analyze(self, image: np.ndarray) -> Dict[str, Any]:
        """执行完整分析

        Args:
            image: 输入图像

        Returns:
            分析结果字典
        """
        results = {
            "ocr": None,
            "ui_detection": None,
            "anomaly_detection": None,
            "image_diff": None,
        }

        # OCR分析
        if self.ocr_enabled:
            results["ocr"] = self.ocr_recognize(image)

        # UI元素检测
        if self.ui_enabled:
            results["ui_detection"] = self.detect_ui_elements(image)

        # 异常检测
        if self.anomaly_enabled:
            results["anomaly_detection"] = self.detect_anomalies(image)

        return results

    def ocr_recognize(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """OCR文字识别

        Args:
            image: 输入图像

        Returns:
            识别结果列表
        """
        if self._ocr_model is None:
            self._init_ocr()

        if self._ocr_model is None:
            return []

        try:
            results = self._ocr_model.ocr(image, cls=True)

            if results is None or len(results) == 0:
                return []

            ocr_results = []
            for result in results:
                if result is None:
                    continue
                for line in result:
                    if line is None:
                        continue
                    box = line[0]
                    text = line[1][0]
                    confidence = line[1][1]

                    ocr_results.append({
                        "text": text,
                        "confidence": float(confidence),
                        "box": box.tolist() if hasattr(box, 'tolist') else box
                    })

            return ocr_results
        except Exception as e:
            print(f"OCR error: {e}")
            return []

    def detect_ui_elements(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """UI元素检测

        Args:
            image: 输入图像

        Returns:
            检测结果列表
        """
        if self._ui_model is None:
            self._init_ui_detection()

        if self._ui_model is None:
            return []

        try:
            conf_threshold = self.ui_config.get("conf_threshold", 0.25)
            results = self._ui_model(image, conf=conf_threshold, verbose=False)

            ui_results = []
            for result in results:
                boxes = result.boxes
                for i in range(len(boxes)):
                    box = boxes[i]
                    ui_results.append({
                        "class": result.names[int(box.cls[0])],
                        "confidence": float(box.conf[0]),
                        "bbox": box.xyxy[0].cpu().numpy().tolist()
                    })

            return ui_results
        except Exception as e:
            print(f"UI detection error: {e}")
            return []

    def detect_anomalies(self, image: np.ndarray) -> Dict[str, Any]:
        """异常检测

        Args:
            image: 输入图像

        Returns:
            异常检测结果
        """
        # 颜色检测
        color_results = self._detect_colors(image)

        return {
            "colors": color_results
        }

    def _detect_colors(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """检测图像中的颜色

        Args:
            image: 输入图像

        Returns:
            检测到的颜色结果
        """
        color_ranges = self.anomaly_config.get("color_ranges", {})
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        results = []
        for color_name, ranges in color_ranges.items():
            if len(ranges) >= 2:
                lower = np.array(ranges[0])
                upper = np.array(ranges[1])

                mask = cv2.inRange(hsv, lower, upper)
                pixel_count = cv2.countNonZero(mask)

                if pixel_count > 0:
                    results.append({
                        "color": color_name,
                        "pixel_count": int(pixel_count),
                        "percentage": float(pixel_count * 100 / (image.shape[0] * image.shape[1]))
                    })

        return results

    def compare_images(self, image1: np.ndarray, image2: np.ndarray) -> Dict[str, Any]:
        """图像对比

        Args:
            image1: 基准图像
            image2: 对比图像

        Returns:
            对比结果
        """
        # 调整图像大小一致
        if image1.shape != image2.shape:
            image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

        # 计算差异
        diff = cv2.absdiff(image1, image2)

        # 计算差异像素数
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        diff_pixels = cv2.countNonZero(thresh)

        total_pixels = image1.shape[0] * image1.shape[1]
        diff_percentage = diff_pixels / total_pixels * 100

        # 计算平均差异
        mean_diff = np.mean(diff)

        return {
            "diff_pixels": int(diff_pixels),
            "diff_percentage": float(diff_percentage),
            "mean_difference": float(mean_diff),
            "is_different": diff_pixels > 0
        }

    def image_to_base64(self, image: np.ndarray, format: str = ".jpg") -> str:
        """将图像转换为base64字符串

        Args:
            image: 输入图像
            format: 图像格式

        Returns:
            base64字符串
        """
        success, encoded = cv2.imencode(format, image)
        if not success:
            return ""

        return base64.b64encode(encoded).decode("utf-8")

    def draw_ocr_results(self, image: np.ndarray, ocr_results: List[Dict]) -> np.ndarray:
        """在图像上绘制OCR结果

        Args:
            image: 输入图像
            ocr_results: OCR结果

        Returns:
            绘制后的图像
        """
        result = image.copy()

        for item in ocr_results:
            box = item.get("box")
            text = item.get("text", "")
            confidence = item.get("confidence", 0)

            if box and len(box) >= 4:
                pts = np.array(box, dtype=np.int32)
                cv2.polylines(result, [pts], True, (0, 255, 0), 2)

                # 绘制文字
                x, y = int(box[0][0]), int(box[0][1])
                cv2.putText(result, f"{text} ({confidence:.2f})",
                           (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return result

    def draw_ui_results(self, image: np.ndarray, ui_results: List[Dict]) -> np.ndarray:
        """在图像上绘制UI检测结果

        Args:
            image: 输入图像
            ui_results: UI检测结果

        Returns:
            绘制后的图像
        """
        result = image.copy()

        for item in ui_results:
            bbox = item.get("bbox", [])
            class_name = item.get("class", "unknown")
            confidence = item.get("confidence", 0)

            if len(bbox) >= 4:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(result, (x1, y1), (x2, y2), (255, 0, 0), 2)

                label = f"{class_name}: {confidence:.2f}"
                cv2.putText(result, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        return result


def create_analyzer(config_path: str = "config.json") -> ImageAnalyzer:
    """创建图像分析器实例

    Args:
        config_path: 配置文件路径

    Returns:
        ImageAnalyzer实例
    """
    return ImageAnalyzer(config_path)
