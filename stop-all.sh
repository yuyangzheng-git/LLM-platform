#!/bin/bash

# LLM Chat Platform 停止脚本
# 使用方法: ./stop-all.sh

echo "🛑 停止LLM Chat Platform"
echo "=============================="

# 读取PID
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "停止后端 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm .backend.pid
    fi
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "停止前端 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm .frontend.pid
    fi
fi

# 备用方案：通过端口杀进程
echo "清理端口..."
lsof -ti:3211 | xargs kill -9 2>/dev/null || true
lsof -ti:3212 | xargs kill -9 2>/dev/null || true

echo "✅ 已停止所有服务"
