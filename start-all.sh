#!/bin/bash

# LLM Chat Platform 完整启动脚本
# 使用方法: ./start-all.sh

set -e

echo "🚀 启动LLM Chat Platform"
echo "=============================="
echo ""

# 启动后端
echo "1️⃣  启动后端..."
cd "$(dirname "$0")/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "   创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 安装依赖（如果需要）
if ! python -c "import beautifulsoup4" 2>/dev/null; then
    echo "   安装依赖..."
    pip install -r requirements.txt -q
fi

# 启动后端（后台运行）
echo "   启动后端服务..."
uvicorn app.main:app --host 0.0.0.0 --port 3211 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
echo "   等待后端启动..."
for i in {1..10}; do
    if curl -s http://localhost:3211/health > /dev/null 2>&1; then
        echo "   ✅ 后端启动成功 (PID: $BACKEND_PID)"
        break
    fi
    sleep 1
done

cd ..

# 启动前端
echo ""
echo "2️⃣  启动前端..."
cd frontend

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "   安装依赖..."
    npm install
fi

echo "   启动前端服务..."
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo "   ✅ 前端启动中 (PID: $FRONTEND_PID)"

cd ..

# 输出信息
echo ""
echo "=============================="
echo "✅ 启动完成！"
echo "=============================="
echo ""
echo "📊 服务信息:"
echo "  后端API:  http://localhost:3211"
echo "  前端应用: http://localhost:3212"
echo "  API文档:  http://localhost:3211/docs"
echo ""
echo "📝 日志文件:"
echo "  后端日志: backend.log"
echo "  前端日志: frontend.log"
echo ""
echo "🛑 停止服务:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  或运行: ./stop-all.sh"
echo ""
echo "🧪 测试建议:"
echo "  1. 访问 http://localhost:3212"
echo "  2. 输入: '今天有什么AI新闻?'"
echo "  3. 输入: '现在几点了?'"
echo "  4. 输入: '北京在哪里?'"
echo ""

# 保存PID到文件
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

echo "提示: 查看实时日志"
echo "  tail -f backend.log"
echo "  tail -f frontend.log"
echo ""
