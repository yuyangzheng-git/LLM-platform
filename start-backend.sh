#!/bin/bash

# LLM Chat Platform 后端启动脚本
# 使用方法: ./start-backend.sh

set -e

echo "🚀 启动LLM Chat Platform后端"
echo "=============================="
echo ""

# 进入后端目录
cd "$(dirname "$0")/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "📦 检查依赖..."
if ! python -c "import beautifulsoup4" 2>/dev/null; then
    echo "⚠️  发现缺少依赖，正在安装..."
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

# 启动后端
echo ""
echo "🚀 启动后端服务器..."
echo "=============================="
echo "访问: http://localhost:3211"
echo "健康检查: http://localhost:3211/health"
echo "API文档: http://localhost:3211/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=============================="
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 3211 --reload
