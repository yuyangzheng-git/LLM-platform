# LLM Chat Platform

生产环境 AI 聊天平台

## 快速部署

```bash
./deploy.sh
```

## 访问

- 应用: http://your-server-ip:3212
- API 文档: http://your-server-ip:3212/docs
- 健康检查: http://your-server-ip:3212/health

## 功能特性

- 多模型支持（OpenAI, Anthropic, Google）
- 实时流式响应
- 工具调用（搜索、时间、地址查询、网站分析）
- 文件上传（图片、PDF）
- 对话历史管理
- PostgreSQL 数据库

## 技术栈

- 后端: FastAPI + Python 3.11
- 前端: React + Vite
- 数据库: PostgreSQL 15
- 反向代理: Nginx
- 容器化: Docker + Docker Compose
