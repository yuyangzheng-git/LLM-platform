FROM llm-chat-platform-frontend:latest as frontend

FROM nginx:alpine

# 从前端镜像复制构建好的文件
COPY --from=frontend /usr/share/nginx/html /usr/share/nginx/html

# 复制 nginx 配置
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

# 暴露 3212 端口
EXPOSE 3212

CMD ["nginx", "-g", "daemon off;"]
