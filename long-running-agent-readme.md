# Long-Running Agent Project Framework

基于 Anthropic 最佳实践的长程智能体项目框架

## 概述

本框架实现了双代理模式：
- **Initializer Agent**: 首次运行，创建项目结构和特性清单
- **Coding Agent**: 后续运行，增量实现功能

## 核心文件

```
.
├── claude_loop.sh          # 主循环脚本
├── init.sh                 # 项目初始化脚本
├── feature_list.json       # 特性清单
├── claude-progress.txt     # 进度日志
├── prompts/                # Prompt 模板
│   ├── initializer_prompt.md
│   └── coding_prompt.md
└── claude_loop_logs/       # 运行日志
```

## 快速开始

```bash
# 初始化git仓库（首次）
git init
git add .
git commit -m "Initial setup"

# 运行5次Claude迭代
./claude_loop.sh 5
```

## 使用方法

```bash
# 基本用法
./claude_loop.sh <次数> [feature文件]

# 示例
./claude_loop.sh 5                    # 循环5次
./claude_loop.sh 3 ./my_features.json  # 指定特性文件
```

## 重要说明

### 嵌套会话问题

在 Claude Code 会话内运行脚本时，需要unset环境变量：

```bash
unset CLAUDECODE
./claude_loop.sh 3
```

或在新的终端会话中运行。

### 特性清单格式

```json
{
  "id": "unique-id",
  "category": "functional",
  "description": "功能描述",
  "steps": ["步骤1", "步骤2"],
  "passes": false,
  "priority": "high"
}
```

**规则**: 只能将 `passes` 从 false 改为 true，禁止删除或修改测试步骤。

## init.sh 命令

```bash
./init.sh              # 启动开发服务器
./init.sh install     # 安装依赖
./init.sh test        # 运行测试
./init.sh status      # 查看项目状态
```

## 文档

- [Anthropic 论文](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic Autonomous Coding 示例](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
