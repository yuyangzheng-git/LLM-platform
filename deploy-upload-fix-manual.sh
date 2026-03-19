#!/bin/bash
# 手动部署指令 - 复制粘贴到服务器执行

cd /opt/llm-chat-platform

# 备份当前配置
echo "备份当前文件..."
cp backend/app/api/files.py backend/app/api/files.py.bak
cp backend/app/config.py backend/app/config.py.bak
cp backend/app/utils/file_validator.py backend/app/utils/file_validator.py.bak

# 解压新文件
echo "应用修复..."
tar xzf llm-chat-upload-fix.tar.gz

# 重新构建
echo "重新构建后端..."
docker compose -f docker-compose.final.yml build backend

# 重启服务
echo "重启服务..."
docker compose -f docker-compose.final.yml restart backend
docker compose -f docker-compose.final.yml restart nginx

# 检查状态
echo "检查服务状态..."
docker compose -f docker-compose.final.yml ps

echo ""
echo "✅ 部署完成！"
echo ""
echo "现在支持的文件类型："
echo "  • DOC, DOCX, XLS, XLSX, PPT, PPTX"
echo "  • CSV, JSON, XML, HTML"
echo "  • 所有图片格式"
echo "  • 文件大小上限: 100MB"
echo ""
