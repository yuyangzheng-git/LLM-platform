#!/bin/bash
# LLM Chat Platform - 快速部署脚本（无Docker）

set -e

echo "========================================="
echo "LLM Chat Platform - 快速部署（无Docker）"
echo "========================================="

cd /home/ubuntu/llm-chat-platform

# 安装Python依赖
echo "安装后端依赖..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 创建必要目录
mkdir -p data uploads logs

# 启动后端（后台运行）
echo "启动后端服务..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 3211 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端PID: $BACKEND_PID"

cd ../frontend

# 安装前端依赖并构建
echo "构建前端..."
npm install
npm run build

# 使用Python简单HTTP服务器提供前端
echo "启动前端服务..."
cd dist
nohup python3 -m http.server 3212 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端PID: $FRONTEND_PID"

echo ""
echo "========================================="
echo "✅ 部署完成！"
echo "========================================="
echo "后端: http://your-server-ip:3211"
echo "前端: http://your-server-ip:3212"
echo ""
echo "后端日志: /home/ubuntu/llm-chat-platform/backend/logs/backend.log"
echo "前端日志: /tmp/frontend.log"
echo ""
echo "停止服务: kill $BACKEND_PID $FRONTEND_PID"
echo "========================================="
