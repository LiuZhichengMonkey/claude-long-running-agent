"""
Web服务器模块
提供MJPEG流媒体、HTTP API和Web界面
"""

import cv2
import json
import os
import time
import threading
from flask import Flask, render_template, Response, request, jsonify, send_from_directory
from typing import Optional

from .camera import CameraCapture
from .analyzer import ImageAnalyzer


app = Flask(__name__,
            template_folder="../templates",
            static_folder="../static")

# 全局实例
camera: Optional[CameraCapture] = None
analyzer: Optional[ImageAnalyzer] = None

# 配置
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
CAPTURE_DIR = "captures"

# 确保捕获目录存在
os.makedirs(CAPTURE_DIR, exist_ok=True)


def init_app():
    """初始化应用"""
    global camera, analyzer

    camera = CameraCapture(CONFIG_PATH)
    analyzer = ImageAnalyzer(CONFIG_PATH)

    return camera, analyzer


def gen_frames():
    """MJPEG流生成器"""
    while True:
        if camera is None or not camera.is_opened():
            time.sleep(0.1)
            continue

        ret, frame = camera.read()
        if not ret:
            continue

        # 编码为JPEG
        ret, jpeg = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        # 生成MJPEG流
        frame_bytes = jpeg.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")


@app.route("/")
def index():
    """主页"""
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    """视频流路由"""
    return Response(gen_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/camera/status")
def camera_status():
    """获取摄像头状态"""
    if camera is None:
        return jsonify({"status": "not_initialized"})

    return jsonify({
        "is_opened": camera.is_opened(),
        "properties": camera.get_properties()
    })


@app.route("/api/camera/open", methods=["POST"])
def camera_open():
    """打开摄像头"""
    global camera

    if camera is None:
        camera = CameraCapture(CONFIG_PATH)

    success = camera.open()

    return jsonify({
        "success": success,
        "message": "Camera opened" if success else "Failed to open camera"
    })


@app.route("/api/camera/close", methods=["POST"])
def camera_close():
    """关闭摄像头"""
    global camera

    if camera is not None:
        camera.close()

    return jsonify({
        "success": True,
        "message": "Camera closed"
    })


@app.route("/api/capture", methods=["POST"])
def capture_image():
    """捕获图像"""
    if camera is None or not camera.is_opened():
        return jsonify({"success": False, "message": "Camera not opened"})

    # 生成文件名
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.jpg"
    filepath = os.path.join(CAPTURE_DIR, filename)

    # 保存图像
    success = camera.capture_image(filepath)

    return jsonify({
        "success": success,
        "filepath": filepath if success else None,
        "message": "Image captured" if success else "Failed to capture image"
    })


@app.route("/api/analyze", methods=["POST"])
def analyze_image():
    """分析图像"""
    if camera is None or not camera.is_opened():
        return jsonify({"success": False, "message": "Camera not opened"})

    ret, frame = camera.read()
    if not ret:
        return jsonify({"success": False, "message": "Failed to read frame"})

    # 执行分析
    results = analyzer.analyze(frame)

    return jsonify({
        "success": True,
        "results": results
    })


@app.route("/api/ocr", methods=["POST"])
def ocr_recognize():
    """OCR识别"""
    if camera is None or not camera.is_opened():
        return jsonify({"success": False, "message": "Camera not opened"})

    ret, frame = camera.read()
    if not ret:
        return jsonify({"success": False, "message": "Failed to read frame"})

    results = analyzer.ocr_recognize(frame)

    return jsonify({
        "success": True,
        "results": results
    })


@app.route("/api/ui-detect", methods=["POST"])
def ui_detect():
    """UI元素检测"""
    if camera is None or not camera.is_opened():
        return jsonify({"success": False, "message": "Camera not opened"})

    ret, frame = camera.read()
    if not ret:
        return jsonify({"success": False, "message": "Failed to read frame"})

    results = analyzer.detect_ui_elements(frame)

    return jsonify({
        "success": True,
        "results": results
    })


@app.route("/api/anomaly", methods=["POST"])
def anomaly_detect():
    """异常检测"""
    if camera is None or not camera.is_opened():
        return jsonify({"success": False, "message": "Camera not opened"})

    ret, frame = camera.read()
    if not ret:
        return jsonify({"success": False, "message": "Failed to read frame"})

    results = analyzer.detect_anomalies(frame)

    return jsonify({
        "success": True,
        "results": results
    })


@app.route("/api/cameras")
def list_cameras():
    """列出可用摄像头"""
    if camera is None:
        camera = CameraCapture(CONFIG_PATH)

    available = camera.get_available_cameras()

    return jsonify({
        "cameras": available
    })


@app.route("/api/config", methods=["GET", "POST"])
def config_api():
    """配置API"""
    if request.method == "POST":
        # 保存配置
        new_config = request.json
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)

        return jsonify({"success": True, "message": "Config saved"})

    # 读取配置
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    return jsonify(config)


@app.route("/captures/<filename>")
def serve_capture(filename):
    """提供捕获的图像"""
    return send_from_directory(CAPTURE_DIR, filename)


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """运行服务器

    Args:
        host: 主机地址
        port: 端口
        debug: 调试模式
    """
    init_app()

    # 尝试打开摄像头
    if camera:
        camera.open()

    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    run_server()
