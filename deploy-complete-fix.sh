#!/bin/bash
# 完整修复部署脚本
# 包含：1. 文件上传修复 2. UI优化 3. 删除对话功能

set -e

cd /opt/llm-chat-platform

echo "================================================"
echo "   LLM Chat Platform - 完整修复部署"
echo "================================================"
echo ""
echo "✨ 修复内容："
echo "  1. 文件上传 - 完全基于扩展名验证"
echo "  2. 合并顶部栏 - 更简洁的UI"
echo "  3. 删除对话 - 鼠标悬停显示删除按钮"
echo ""

# 解压文件
echo "📦 步骤 1/5: 解压更新包..."
tar xzf llm-chat-complete-fix.tar.gz
echo "✅ 文件已解压"
echo ""

# 重新构建前端
echo "🔨 步骤 2/5: 重新构建前端..."
docker compose -f docker-compose.final.yml build frontend
echo "✅ 前端构建完成"
echo ""

# 重新构建后端
echo "🔨 步骤 3/5: 重新构建后端..."
docker compose -f docker-compose.final.yml build backend
echo "✅ 后端构建完成"
echo ""

# 重新构建 Nginx
echo "🔨 步骤 4/5: 重新构建 Nginx..."
docker compose -f docker-compose.final.yml build nginx
echo "✅ Nginx 构建完成"
echo ""

# 重启所有服务
echo "🔄 步骤 5/5: 重启所有服务..."
docker compose -f docker-compose.final.yml down
docker compose -f docker-compose.final.yml up -d
echo "✅ 服务已启动"
echo ""

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
docker compose -f docker-compose.final.yml ps
echo ""

echo "================================================"
echo "✅ 部署完成！"
echo "================================================"
echo ""
echo "📝 修复详情："
echo ""
echo "1. 📁 文件上传修复："
echo "   • 完全移除 MIME 类型检查"
echo "   • 只验证文件扩展名"
echo "   • 支持: .doc, .docx, .xls, .xlsx, .ppt, .pptx, .pdf, .png, .jpg, .csv, .txt, .md 等"
echo ""
echo "2. 🎨 UI优化："
echo "   • 合并两个顶部栏为一个"
echo "   • 顶栏显示当前选择的模型"
echo "   • 更简洁的界面设计"
echo ""
echo "3. 🗑️ 删除对话功能："
echo "   • 在对话历史侧边栏"
echo "   • 鼠标悬停在对话上会显示删除按钮"
echo "   • 删除前会有确认提示"
echo ""
echo "🧪 测试建议："
echo "   1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "   2. 访问 http://your-server-ip:3212"
echo "   3. 测试上传 .docx 或 .xlsx 文件"
echo "   4. 打开对话历史，悬停查看删除按钮"
echo ""
echo "🔍 查看日志："
echo "   docker logs llm-chat-backend --tail 50"
echo "   docker logs llm-chat-nginx --tail 50"
echo ""
