#!/bin/bash

################################################################################
# 项目初始化启动脚本
# 用于长时间运行项目的环境启动
#
# 使用方法:
#   ./init.sh              # 启动开发服务器
#   ./init.sh test         # 运行测试
#   ./init.sh install      # 安装依赖
#   ./init.sh status      # 查看项目状态
#
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 项目配置
PROJECT_NAME="demo-project"
DEV_PORT=3000

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  $PROJECT_NAME 初始化脚本${NC}"
echo -e "${BLUE}========================================${NC}"

# 显示帮助
show_help() {
    echo ""
    echo "用法: ./init.sh [command]"
    echo ""
    echo "命令:"
    echo "  (无参数)   启动开发服务器"
    echo "  install    安装项目依赖"
    echo "  test       运行测试"
    echo "  status     查看项目状态"
    echo "  git-log    查看最近的git提交"
    echo "  progress   查看项目进度"
    echo "  help       显示帮助"
    echo ""
}

# 安装依赖
do_install() {
    echo -e "${YELLOW}安装项目依赖...${NC}"

    if [ -f "package.json" ]; then
        npm install
    elif [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    elif [ -f "go.mod" ]; then
        go mod download
    else
        echo -e "${YELLOW}未找到依赖配置文件，跳过安装${NC}"
    fi

    echo -e "${GREEN}✅ 依赖安装完成${NC}"
}

# 查看项目状态
do_status() {
    echo -e "${BLUE}📊 项目状态${NC}"
    echo ""

    # Git状态
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${GREEN}Git仓库: 已初始化${NC}"
        echo "  分支: $(git branch --show-current)"
        echo "  提交: $(git log --oneline -1)"
        echo "  状态: $(git status --short)"
    else
        echo -e "${RED}Git仓库: 未初始化${NC}"
    fi
    echo ""

    # 特性清单状态
    if [ -f "feature_list.json" ]; then
        echo -e "${BLUE}📋 特性清单状态:${NC}"
        total=$(grep -o '"id"' feature_list.json | wc -l)
        completed=$(grep '"passes": true' feature_list.json | wc -l)
        echo "  总特性: $total"
        echo "  已完成: $completed"
        echo "  进行中: $((total - completed))"
    fi
    echo ""

    # 最近进度
    if [ -f "claude-progress.txt" ]; then
        echo -e "${BLUE}📝 最近进度:${NC}"
        tail -10 claude-progress.txt
    fi
}

# 查看git日志
do_git_log() {
    echo -e "${BLUE}📜 最近Git提交:${NC}"
    git log --oneline -10
}

# 查看进度
do_progress() {
    echo -e "${BLUE}📝 项目进度:${NC}"
    if [ -f "claude-progress.txt" ]; then
        cat claude-progress.txt
    else
        echo "暂无进度记录"
    fi
}

# 启动开发服务器
do_start() {
    echo -e "${YELLOW}启动开发服务器...${NC}"

    if [ -f "package.json" ]; then
        # Node.js项目
        if [ -f "vite.config.js" ] || [ -f "vite.config.ts" ]; then
            npm run dev -- --port $DEV_PORT &
        elif [ -f "next.config.js" ]; then
            npm run dev -- -p $DEV_PORT &
        else
            npm start &
        fi
    elif [ -f "manage.py" ]; then
        # Django项目
        python manage.py runserver $DEV_PORT &
    elif [ -f "main.go" ]; then
        # Go项目
        go run main.go &
    else
        echo -e "${YELLOW}未识别的项目类型，请手动启动${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ 开发服务器已启动: http://localhost:$DEV_PORT${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"

    # 等待用户中断
    wait
}

# 运行测试
do_test() {
    echo -e "${YELLOW}运行测试...${NC}"

    if [ -f "package.json" ]; then
        npm test
    elif [ -f "requirements.txt" ]; then
        pytest
    elif [ -f "go.mod" ]; then
        go test ./...
    else
        echo -e "${YELLOW}未找到测试配置${NC}"
    fi
}

# 主逻辑
case "${1:-start}" in
    install)
        do_install
        ;;
    status)
        do_status
        ;;
    git-log)
        do_git_log
        ;;
    progress)
        do_progress
        ;;
    test)
        do_test
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        do_start
        ;;
esac
