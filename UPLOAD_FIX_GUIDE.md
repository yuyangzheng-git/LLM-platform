# 文件上传修复 - 手动部署指南

## 问题说明

文件上传"经常不成功"的原因：
1. ❌ 后端只支持有限的文件类型（PNG, JPEG, PDF, TXT, MD）
2. ❌ 前端允许上传 DOC, DOCX, CSV, XLSX 等，但后端会拒绝
3. ❌ 文件大小限制只有 10MB，太小
4. ❌ 上传失败时没有详细错误提示

## 修复内容

✅ **扩展文件类型支持：**
- 图片: PNG, JPEG, GIF, WebP, BMP, SVG
- 文档: PDF, **DOC, DOCX, XLS, XLSX, PPT, PPTX**
- 文本: TXT, MD, **CSV**, HTML, JSON, XML

✅ **增加文件大小限制：**
- 从 10MB → **100MB**

✅ **改进错误提示：**
- 英文 → 中文
- 详细的文件名和错误信息
- 批量上传时显示每个失败文件的原因

## 自动部署（推荐）

```bash
./fix-upload-deploy.sh
```

需要输入服务器密码：`your_password`

## 手动部署

如果自动部署失败，请按以下步骤手动操作：

### 1. 传输文件到服务器

```bash
scp llm-chat-upload-fix.tar.gz ubuntu@your-server-ip:/opt/llm-chat-platform/
```

### 2. SSH 登录服务器

```bash
ssh ubuntu@your-server-ip
# 密码: your_password
```

### 3. 解压并重启服务

```bash
cd /opt/llm-chat-platform

# 解压文件
tar xzf llm-chat-upload-fix.tar.gz

# 重新构建后端
docker compose -f docker-compose.final.yml build backend

# 重启服务
docker compose -f docker-compose.final.yml restart backend
docker compose -f docker-compose.final.yml restart nginx

# 查看服务状态
docker compose -f docker-compose.final.yml ps

# 查看后端日志（检查是否有错误）
docker logs llm-chat-backend --tail 50
```

## 测试验证

部署完成后，请测试以下场景：

### 1. Word 文档上传
- 创建一个 `.docx` 文件
- 在聊天界面上传
- ✅ 应该显示进度条并成功上传

### 2. Excel 表格上传
- 准备一个 `.xlsx` 文件
- 上传测试
- ✅ 应该成功并显示"已上传"标记

### 3. 大文件上传
- 准备一个 50-80MB 的文件
- 上传测试
- ✅ 应该显示进度条并成功上传

### 4. 错误提示测试
- 尝试上传超过 100MB 的文件
- ✅ 应该显示中文错误提示："文件大小 XXX.XMB 超过限制 100MB"

### 5. 不支持的文件类型
- 尝试上传 `.exe` 或 `.zip` 文件
- ✅ 应该显示："文件类型 XXX 不支持"

## 查看日志

如果上传仍然失败，查看详细日志：

```bash
# 后端日志
docker logs llm-chat-backend --tail 100 -f

# Nginx 日志
docker logs llm-chat-nginx --tail 100 -f
```

查找以下关键词：
- `File upload failed`
- `文件类型`
- `文件大小`
- `部分文件上传失败`

## 回滚方案

如果新版本有问题，可以回滚：

```bash
cd /opt/llm-chat-platform

# 重启到之前的镜像
docker compose -f docker-compose.final.yml restart

# 如果需要完全重新部署，使用之前的备份
# tar xzf llm-chat-deploy-final.tar.gz
```

## 技术细节

### 修改的文件：

1. **backend/app/api/files.py** (行 61-110)
   - 增加失败文件记录
   - 批量上传时返回详细错误

2. **backend/app/config.py** (行 25-49)
   - MAX_FILE_SIZE: 10MB → 100MB
   - ALLOWED_FILE_TYPES: 扩展到 17 种类型

3. **backend/app/utils/file_validator.py** (行 10-52)
   - 扩展 allowed_extensions 字典
   - 错误提示改为中文

4. **.env.production** (行 15-18)
   - 更新环境变量配置

## 常见问题

### Q: 为什么还是上传不成功？
A: 检查以下几点：
1. 清除浏览器缓存（Ctrl+Shift+R）
2. 检查文件是否超过 100MB
3. 检查文件类型是否在支持列表中
4. 查看后端日志确认具体错误

### Q: 如何确认新版本已生效？
A: 尝试上传一个 `.xlsx` 文件：
- ✅ 成功 = 新版本已生效
- ❌ 失败并显示"文件类型不支持" = 旧版本仍在运行

### Q: 上传进度卡在某个百分比？
A: 可能是网络问题或文件过大：
1. 检查网络连接
2. 尝试上传较小的文件
3. 查看 Nginx 日志是否有超时错误
