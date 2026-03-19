# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# 接收构建参数
ARG VITE_API_BASE_URL=http://localhost:3211

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# 设置环境变量用于构建
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3212

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
