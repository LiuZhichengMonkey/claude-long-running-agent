# Claude 长程智能体项目框架

基于 Anthropic 最佳实践构建的长时间运行项目框架。

## 参考资料

- [Anthropic 论文: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic Autonomous Coding 示例](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)

## 目录结构

```
.
├── claude_loop.sh          # 主循环脚本 - 循环调用Claude
├── init.sh                 # 项目初始化脚本
├── feature_list.json       # 特性清单 (Anthropic格式)
├── claude-progress.txt     # 进度日志
├── prompts/                # Prompt模板目录
│   ├── initializer_prompt.md   # 初始化代理Prompt
│   └── coding_prompt.md        # 编码代理Prompt
└── claude_loop_logs/      # 运行日志目录
```

## 快速开始

### 1. 确保是Git仓库

```bash
git init
git add .
git commit -m "Initial setup"
```

### 2. 自定义特性清单

编辑 `feature_list.json`，添加你需要实现的功能。

### 3. 自定义Prompt（可选）

编辑 `prompts/initializer_prompt.md` 和 `prompts/coding_prompt.md`。

### 4. 运行长程任务

```bash
# 循环调用Claude 5次
./claude_loop.sh 5

# 指定特性文件
./claude_loop.sh 3 ./my_features.json
```

## 核心概念

### 双代理模式

| 代理类型 | 使用时机 | 职责 |
|---------|---------|------|
| **Initializer Agent** | 首次运行 | 搭建环境、创建特性清单 |
| **Coding Agent** | 后续运行 | 增量开发、添加功能 |

### 特性清单格式

```json
{
  "id": "unique-id",
  "category": "functional",
  "description": "功能描述",
  "steps": ["步骤1", "步骤2", "步骤3"],
  "passes": false,
  "priority": "high"
}
```

**关键规则**：
- 每次会话只能将 `passes` 从 `false` 改为 `true`
- **禁止**删除、编辑描述或修改测试步骤

### Prompt模板

- `prompts/initializer_prompt.md`: 首次运行时使用的Prompt
- `prompts/coding_prompt.md`: 后续运行时使用的Prompt

## Git 工作流

基于 Anthropic Autonomous Coding 示例：

### 会话开始
```bash
pwd                           # 确认工作目录
git log --oneline -10         # 查看最近提交
cat claude-progress.txt       # 查看进度
```

### 会话进行中
- 每次只处理一个特性
- 通过实际UI测试

### 会话结束
```bash
# 更新feature_list.json (passes: true)
# 更新claude-progress.txt
git add -A
git commit -m "Session N: 完成的功能描述"
```

## init.sh 命令

```bash
./init.sh              # 启动开发服务器
./init.sh install     # 安装依赖
./init.sh test        # 运行测试
./init.sh status      # 查看项目状态
./init.sh git-log     # 查看git提交
./init.sh progress    # 查看进度
```

## 使用示例

### 完整工作流

```bash
# 1. 初始化git仓库
git init
git add .
git commit -m "Initial setup"

# 2. 自定义feature_list.json
# (编辑你的特性清单)

# 3. 运行5次Claude迭代
./claude_loop.sh 5

# 4. 查看最终状态
./init.sh status
```

## 预期时间

- **首次会话**：初始化代理生成详细的特性清单，需要几分钟
- **后续会话**：每次编码迭代可能需要 5-15 分钟
- **完整应用**：根据功能数量，可能需要数小时

## 日志文件

- 运行日志：`./claude_loop_logs/claude_loop_YYYYMMDD_HHMMSS.log`
- 进度日志：`./claude-progress.txt`
