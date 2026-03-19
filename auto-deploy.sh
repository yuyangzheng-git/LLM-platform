#!/bin/bash
# 自动部署脚本 - 从本地到服务器一键部署
# 使用方法: ./auto-deploy.sh

set -e

SERVER="ubuntu@your-server-ip"
REMOTE_DIR="/opt/llm-chat-platform"
PACKAGE="llm-chat-complete-fix.tar.gz"

echo "================================================"
echo "   LLM Chat Platform - 自动部署到服务器"
echo "================================================"
echo ""
echo "📦 部署内容："
echo "  1. 文件上传修复（完全基于扩展名验证）"
echo "  2. UI优化（合并顶栏）"
echo "  3. 删除对话功能"
echo ""
echo "🎯 目标服务器: $SERVER"
echo ""

# 检查文件是否存在
if [ ! -f "$PACKAGE" ]; then
    echo "❌ 错误: $PACKAGE 不存在"
    exit 1
fi

echo "步骤 1/2: 传输文件到服务器..."
echo "请输入服务器密码: your_password"
scp "$PACKAGE" "$SERVER:$REMOTE_DIR/"

echo ""
echo "步骤 2/2: 在服务器上执行部署..."
echo "请再次输入服务器密码..."

ssh "$SERVER" << 'ENDSSH'
cd /opt/llm-chat-platform

echo "================================================"
echo "   开始部署"
echo "================================================"
echo ""

# 解压文件
echo "📦 1/5: 解压更新包..."
tar xzf llm-chat-complete-fix.tar.gz
echo "✅ 文件已解压"
echo ""

# 重新构建前端
echo "🔨 2/5: 重新构建前端..."
docker compose -f docker-compose.final.yml build frontend
echo "✅ 前端构建完成"
echo ""

# 重新构建后端
echo "🔨 3/5: 重新构建后端..."
docker compose -f docker-compose.final.yml build backend
echo "✅ 后端构建完成"
echo ""

# 重新构建 Nginx
echo "🔨 4/5: 重新构建 Nginx..."
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

echo "================================================"
echo "✅ 部署完成！"
echo "================================================"
echo ""
echo "🧪 测试步骤："
echo "  1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "  2. 访问 http://your-server-ip:3212"
echo "  3. 测试上传 .docx 或 .xlsx 文件"
echo "  4. 查看顶部只有一个栏（右侧显示模型）"
echo "  5. 打开对话历史，悬停查看删除按钮"
echo ""
echo "🔍 查看日志："
echo "  docker logs llm-chat-backend --tail 50"
echo "  docker logs llm-chat-nginx --tail 30"
echo ""

ENDSSH

echo ""
echo "================================================"
echo "✅ 部署完成！"
echo "================================================"
echo ""
echo "⚠️  重要：清除浏览器缓存后再测试"
echo "   Windows/Linux: Ctrl + Shift + R"
echo "   Mac: Cmd + Shift + R"
echo ""
