# Long-Running Agent Project Framework

基于 Anthropic 最佳实践的长程智能体项目框架

## 核心文件

- `claude_loop.sh` - 主循环脚本
- `init.sh` - 项目初始化脚本
- `feature_list.json` - 特性清单
- `claude-progress.txt` - 进度日志
- `prompts/` - Prompt 模板
- `LONG_RUNNING_PROJECT.md` - 框架说明

## 使用方法

```bash
# 运行5次Claude迭代
./claude_loop.sh 5
```

## 文档

- [Anthropic 论文](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic Autonomous Coding 示例](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
