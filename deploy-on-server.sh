#!/bin/bash
# 服务器端部署脚本 - 直接在服务器上运行

cd /opt/llm-chat-platform

echo "================================================"
echo "   LLM Chat Platform - 服务器端部署"
echo "================================================"
echo ""

# 检查文件是否存在
if [ ! -f "llm-chat-complete-fix.tar.gz" ]; then
    echo "❌ 错误: llm-chat-complete-fix.tar.gz 不存在"
    echo "请先传输文件到服务器"
    exit 1
fi

# 解压文件
echo "📦 1/5: 解压更新包..."
tar xzf llm-chat-complete-fix.tar.gz
echo "✅ 文件已解压"
echo ""

# 重新构建前端
echo "🔨 2/5: 重新构建前端（约30秒）..."
docker compose -f docker-compose.final.yml build frontend
echo "✅ 前端构建完成"
echo ""

# 重新构建后端
echo "🔨 3/5: 重新构建后端（约1分钟）..."
docker compose -f docker-compose.final.yml build backend
echo "✅ 后端构建完成"
echo ""

# 重新构建 Nginx
echo "🔨 4/5: 重新构建 Nginx（约10秒）..."
docker compose -f docker-compose.final.yml build nginx
echo "✅ Nginx 构建完成"
echo ""

# 重启所有服务
echo "🔄 5/5: 重启所有服务..."
docker compose -f docker-compose.final.yml down
docker compose -f docker-compose.final.yml up -d
echo "✅ 服务已启动"
echo ""

# 等待服务启动
echo "⏳ 等待服务启动（5秒）..."
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
docker compose -f docker-compose.final.yml ps
echo ""

# 检查后端日志
echo "📋 后端日志（最近10行）："
docker logs llm-chat-backend --tail 10
echo ""

echo "================================================"
echo "✅ 部署完成！"
echo "================================================"
echo ""
echo "🧪 现在请测试："
echo ""
echo "1. 清除浏览器缓存"
echo "   Windows/Linux: Ctrl + Shift + R"
echo "   Mac: Cmd + Shift + R"
echo ""
echo "2. 访问 http://your-server-ip:3212"
echo ""
echo "3. 测试功能："
echo "   ✅ 上传 .docx 或 .xlsx 文件"
echo "   ✅ 查看顶部只有一个栏"
echo "   ✅ 打开对话历史，悬停查看删除按钮"
echo ""
echo "🔍 查看完整日志："
echo "   docker logs llm-chat-backend --tail 50"
echo "   docker logs llm-chat-nginx --tail 30"
echo ""
