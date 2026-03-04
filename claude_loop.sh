#!/bin/bash

################################################################################
# Claude循环调用脚本 - 长程智能体框架
# 基于 Anthropic 最佳实践: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
#
# 功能:
#   - 循环调用claude指定次数
#   - 每次调用使用初始prompt让claude从task/feature文件读取任务并执行
#   - 会话开始时阅读git日志和进度文件
#   - 会话结束时更新进度文件和git提交
#   - 自动记录日志到 ./claude_loop_logs/ 目录
#
# 用法:
#   ./claude_loop.sh <次数> [feature文件路径]
#
# 参数说明:
#   次数         - 必须，指定要调用claude的次数
#   feature文件  - 可选，默认为 ./feature_list.json
#
# 示例:
#   ./claude_loop.sh 5                              # 循环5次
#   ./claude_loop.sh 3 ./my_features.json          # 循环3次，使用指定文件
#
################################################################################

# 检查参数
if [ -z "$1" ]; then
    echo "用法: $0 <循环次数> [feature文件路径]"
    echo ""
    echo "参数说明:"
    echo "  循环次数   - 必须，指定要调用claude的次数"
    echo "  feature文件 - 可选，默认为 ./feature_list.json"
    echo ""
    echo "示例:"
    echo "  $0 5                    # 循环5次，使用默认feature文件"
    echo "  $0 3 ./my_features.json  # 循环3次，使用指定文件"
    exit 1
fi

LOOP_COUNT=$1
FEATURE_FILE=${2:-"./feature_list.json"}

# Prompt文件路径
PROMPTS_DIR="./prompts"
INITIALIZER_PROMPT="$PROMPTS_DIR/initializer_prompt.md"
CODING_PROMPT="$PROMPTS_DIR/coding_prompt.md"

# 读取prompt文件或使用默认模板
load_prompt() {
    local prompt_file=$1
    if [ -f "$prompt_file" ]; then
        cat "$prompt_file"
    else
        # 默认fallback prompt
        cat <<'EOF'
你是一个长程智能体项目的Coding Agent。请按以下步骤执行：

1. 首先阅读项目状态：
   - 运行 'pwd' 确认工作目录
   - 运行 'git log --oneline -10' 查看最近提交
   - 如果有 'claude-progress.txt' 文件，阅读它了解进度

2. 读取特性清单，找到一个未完成的特性（passes: false）

3. 实现这个特性：
   - 每次只处理一个特性（增量开发）
   - 编写代码实现功能

4. 端到端验证：
   - 通过实际UI测试
   - 截取屏幕截图验证

5. 完成后：
   - 更新特性清单文件，将该特性的 "passes" 设为 true
   - 在 claude-progress.txt 中记录完成的工作
   - 使用描述性信息提交到 git
   - 退出让主脚本继续
EOF
    fi
}

# 判断是否为首次运行
is_first_run() {
    if [ -f "$FEATURE_FILE" ]; then
        local completed_count=$(grep '"passes": true' "$FEATURE_FILE" | wc -l)
        if [ "$completed_count" -eq 0 ]; then
            return 0  # 首次运行
        fi
        return 1  # 非首次
    fi
    return 0  # 文件不存在，视为首次
}

# 选择合适的prompt
if is_first_run; then
    log "📌 首次运行，使用 Initializer Agent Prompt"
    INITIAL_PROMPT=$(load_prompt "$INITIALIZER_PROMPT")
else
    log "📌 继续运行，使用 Coding Agent Prompt"
    INITIAL_PROMPT=$(load_prompt "$CODING_PROMPT")
fi

# 日志文件
LOG_DIR="./claude_loop_logs"
LOG_FILE="$LOG_DIR/claude_loop_$(date +%Y%m%d_%H%M%S).log"
PROGRESS_FILE="./claude-progress.txt"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 打印带时间戳的日志
log() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1"
    echo "[$timestamp] $1" >> "$LOG_FILE"
}

# 打印带时间的进度信息
progress_info() {
    local iteration=$1
    local total=$2
    local percent=$(($iteration * 100 / $total))
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] 📊 进度: $iteration/$total ($percent%)"
    echo "[$timestamp] 📊 进度: $iteration/$total ($percent%)" >> "$LOG_FILE"
}

# 打印分隔线
print_separator() {
    echo "----------------------------------------"
    echo "----------------------------------------" >> "$LOG_FILE"
}

# 打印会话开始信息（基于文章的最佳实践）
print_session_start() {
    local iteration=$1
    print_separator
    log "▶️  会话 $iteration 开始"
    log "📂 工作目录: $(pwd)"

    # 基于文章：阅读git日志和进度文件
    if [ "$IS_GIT_REPO" = true ]; then
        log "📜 最近Git提交:"
        git log --oneline -5 >> "$LOG_FILE" 2>&1
    fi

    if [ -f "$PROGRESS_FILE" ]; then
        log "📝 当前进度:"
        tail -5 "$PROGRESS_FILE" >> "$LOG_FILE" 2>&1
    fi

    if [ -f "$FEATURE_FILE" ]; then
        log "📋 特性文件: $FEATURE_FILE"
    fi

    print_separator
}

# 初始化
print_separator
log "🚀 开始 Claude 长程智能体任务"
log "📝 循环次数: $LOOP_COUNT"
log "📁 特性文件: $FEATURE_FILE"
log "📄 日志文件: $LOG_FILE"
print_separator

# 检查feature文件是否存在
if [ ! -f "$FEATURE_FILE" ]; then
    log "⚠️  警告: 特性文件不存在: $FEATURE_FILE"
    log "⚠️  将继续执行但不读取特性文件"
fi

# 检查是否是git仓库
IS_GIT_REPO=false
if git rev-parse --git-dir > /dev/null 2>&1; then
    IS_GIT_REPO=true
    log "✅ 检测到Git仓库"
else
    log "⚠️  警告: 不是Git仓库，将跳过commit"
fi

# 读取并显示当前特性状态
show_feature_status() {
    if [ -f "$FEATURE_FILE" ]; then
        local total=$(grep -o '"id"' "$FEATURE_FILE" | wc -l)
        local completed=$(grep '"passes": true' "$FEATURE_FILE" | wc -l)
        log "📊 特性状态: $completed/$total 已完成"
    fi
}

# 更新进度文件
update_progress() {
    local iteration=$1
    local work_done=$2

    if [ -f "$PROGRESS_FILE" ]; then
        local timestamp=$(date "+%Y-%m-%d %H:%M")
        echo "" >> "$PROGRESS_FILE"
        echo "[$timestamp] - 会话$iteration" >> "$PROGRESS_FILE"
        echo "- 完成工作: $work_done" >> "$PROGRESS_FILE"
        echo "----------------------------------------" >> "$PROGRESS_FILE"
    fi
}

# Git提交函数 - 基于Anthropic Autonomous Coding最佳实践
commit_changes() {
    local iteration=$1

    if [ "$IS_GIT_REPO" = false ]; then
        log "[会话 $iteration] 跳过提交 (非Git仓库)"
        return 0
    fi

    # 检查是否有变更
    if ! git diff --quiet 2>/dev/null; then
        log "[会话 $iteration] 正在提交变更..."

        # 添加所有变更
        git add -A 2>/dev/null

        # 基于Anthropic示例：生成描述性提交信息
        local commit_msg="Session $iteration: Progress update"

        # 获取本次会话新完成的特性
        if [ -f "$FEATURE_FILE" ]; then
            # 提取最新标记为passes: true的特性描述
            local recent_completed=$(grep -B3 '"passes": true' "$FEATURE_FILE" 2>/dev/null | grep '"description"' | tail -1 | sed 's/.*"description": "\(.*\)".*/\1/')
            if [ -n "$recent_completed" ]; then
                # 截断过长的描述
                if [ ${#recent_completed} -gt 50 ]; then
                    recent_completed="${recent_completed:0:47}..."
                fi
                commit_msg="Session $iteration: $recent_completed"
            fi
        fi

        # 提交
        if git commit -m "$commit_msg" 2>/dev/null; then
            log "[会话 $iteration] ✅ 提交成功: $commit_msg"
            # 确保代码可合并
            log "[会话 $iteration] 💡 代码已准备好可合并到主分支"
            return 0
        else
            log "[会话 $iteration] ❌ 提交失败"
            return 1
        fi
    else
        log "[会话 $iteration] 没有变更需要提交"
        return 0
    fi
}

# 检查代码是否可合并（基于文章）
check_mergeable() {
    if [ "$IS_GIT_REPO" = true ]; then
        # 检查是否有未解决的合并
        if git diff --check > /dev/null 2>&1; then
            log "✅ 代码状态良好，可以合并"
            return 0
        else
            log "⚠️  代码有冲突或问题"
            return 1
        fi
    fi
}

# 主循环
SUCCESS_COUNT=0
FAIL_COUNT=0

show_feature_status

for i in $(seq 1 $LOOP_COUNT); do
    # 基于文章：会话开始时读取git日志和进度文件
    print_session_start $i
    progress_info $i $LOOP_COUNT

    log "💬 调用Claude..."

    # 调用claude
    if command -v claude &> /dev/null; then
        claude --print "$INITIAL_PROMPT" >> "$LOG_FILE" 2>&1
        CLAUDE_EXIT_CODE=$?
    else
        log "❌ 错误: claude命令不可用"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
        log "✅ 会话 $i - Claude调用成功"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

        # 基于文章：更新进度文件
        update_progress $i "Claude task completed"
    else
        log "❌ 会话 $i - Claude调用失败，退出码: $CLAUDE_EXIT_CODE"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    # 基于文章：结束会话时提交变更
    commit_changes $i

    # 基于文章：确保代码可合并
    check_mergeable

    # 显示当前状态
    show_feature_status

    print_separator
done

# 最终总结
print_separator
log "📊 任务完成总结"
log "✅ 成功: $SUCCESS_COUNT/$LOOP_COUNT"
log "❌ 失败: $FAIL_COUNT/$LOOP_COUNT"
log "📄 日志文件: $LOG_FILE"
log "📝 进度文件: $PROGRESS_FILE"

# 显示特性完成状态
if [ -f "$FEATURE_FILE" ]; then
    local total=$(grep -o '"id"' "$FEATURE_FILE" | wc -l)
    local completed=$(grep '"passes": true' "$FEATURE_FILE" | wc -l)
    log "📋 特性完成: $completed/$total"
fi
print_separator

# 返回适当的退出码
if [ $FAIL_COUNT -eq 0 ]; then
    exit 0
else
    exit 1
fi
