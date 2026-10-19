# Multi-stage build for Python backend
FROM python:3.11-slim as builder

ARG DEBIAN_MIRROR=mirrors.aliyun.com

WORKDIR /app

# Install system dependencies
RUN sed -i "s|deb.debian.org|${DEBIAN_MIRROR}|g" /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

ARG DEBIAN_MIRROR=mirrors.aliyun.com

WORKDIR /app

# Install runtime dependencies
RUN sed -i "s|deb.debian.org|${DEBIAN_MIRROR}|g" /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y \
    libmagic1 \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app ./app

# Create directories
RUN mkdir -p /app/data /app/uploads /app/logs

# Expose port
EXPOSE 3211

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3211"]
