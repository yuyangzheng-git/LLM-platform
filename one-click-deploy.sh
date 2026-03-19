#!/bin/bash
# 一键部署 - 请直接运行此脚本

echo "================================================"
echo "   开始部署到服务器"
echo "================================================"
echo ""
echo "请在提示时输入服务器密码"
echo ""

# 步骤1: 传输文件
echo "步骤 1/3: 传输部署包..."
scp llm-chat-complete-fix.tar.gz ubuntu@your-server-ip:/opt/llm-chat-platform/
if [ $? -ne 0 ]; then
    echo "❌ 文件传输失败"
    exit 1
fi
echo "✅ 部署包已传输"
echo ""

# 步骤2: 传输脚本
echo "步骤 2/3: 传输部署脚本..."
scp deploy-on-server.sh ubuntu@your-server-ip:/opt/llm-chat-platform/
if [ $? -ne 0 ]; then
    echo "❌ 脚本传输失败"
    exit 1
fi
echo "✅ 部署脚本已传输"
echo ""

# 步骤3: 执行部署
echo "步骤 3/3: 在服务器上执行部署..."
echo "请再次输入密码..."
ssh ubuntu@your-server-ip 'bash -s' < /tmp/deploy_commands.sh

echo ""
echo "================================================"
echo "✅ 部署完成！"
echo "================================================"
echo ""
echo "⚠️  重要提示："
echo "1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "2. 访问 http://your-server-ip:3212"
echo "3. 测试上传 .docx 或 .xlsx 文件"
echo ""
