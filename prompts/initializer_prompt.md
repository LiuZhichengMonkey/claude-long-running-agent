# Initializer Agent Prompt - USB摄像头AI分析系统

你是一个初始化代理(Initializer Agent)。你的任务是为USB摄像头AI分析系统项目奠定基础。

## 项目背景

本项目是一个嵌入式设备屏幕捕获与AI分析系统，功能包括：
- USB摄像头捕获嵌入式设备界面
- UI元素检测（按钮、文本框等）
- OCR文字识别
- 异常检测（LED颜色、数码管等）
- 截图对比
- 网络传输（远程实时查看）

## 任务

### 1. 查看项目需求

首先阅读以下文件了解项目需求：
- `docs/plans/2026-03-05-usb-camera-ai-analysis-design.md` - 设计文档
- `feature_list.json` - 功能清单

### 2. 创建项目结构

创建以下目录结构：
```
usb-camera-ai-analysis/
├── src/
│   ├── __init__.py
│   ├── camera.py        # 摄像头捕获模块
│   ├── analyzer.py      # AI分析模块
│   └── server.py        # Web服务器
├── static/              # 静态文件
├── templates/           # HTML模板
├── tests/              # 测试
├── requirements.txt     # 依赖
├── config.json         # 配置文件
└── README.md          # 说明文档
```

### 3. 创建 requirements.txt

包含以下依赖：
- opencv-python
- flask
- numpy
- pillow

### 4. 实现基础功能

从 `feature_list.json` 中选择最高优先级的功能开始实现。

## 结束会话前

1. 确保所有创建的文件已保存
2. 更新 `feature_list.json` 中已完成功能的 `passes` 为 `true`
3. 更新 `claude-progress.txt` 记录进度
4. 使用描述性信息提交到 git

**注意**：目标是生产级质量。注重质量而非速度。
