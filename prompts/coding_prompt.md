# Coding Agent Prompt - USB摄像头AI分析系统

你是一个编码代理(Coding Agent)。你的任务是在现有USB摄像头AI分析系统项目基础上增量开发。

## 项目背景

本项目是一个嵌入式设备屏幕捕获与AI分析系统：
- USB摄像头捕获嵌入式设备界面
- UI元素检测、OCR文字识别、异常检测、截图对比
- 网络传输（远程实时查看）

## 执行步骤

### 1. 了解项目状态
- 运行 `pwd` 确认工作目录
- 阅读 `docs/plans/2026-03-05-usb-camera-ai-analysis-design.md` 了解设计
- 阅读 `feature_list.json` 了解待完成任务
- 运行 `git log --oneline -10` 查看最近提交
- 阅读 `claude-progress.txt` 了解进度

### 2. 查看项目结构

检查当前项目目录结构：
```
usb-camera-ai-analysis/
├── src/
├── static/
├── templates/
├── tests/
├── requirements.txt
└── config.json
```

如果目录不存在，先创建基础结构。

### 3. 选择一个特性

从 `feature_list.json` 中选择优先级最高的 `passes: false` 的特性。

### 4. 实现特性

- 编写代码实现功能
- 遵循项目代码规范

### 5. 更新文件

完成后：
1. 更新 `feature_list.json`，将该特性的 `passes` 改为 `true`
2. 更新 `claude-progress.txt` 记录完成的工作

### 6. Git提交

使用描述性信息提交到 git，格式：`功能名称 - 描述`

## 关键规则

- 每次只处理一个特性（增量开发）
- 目标是生产级质量
