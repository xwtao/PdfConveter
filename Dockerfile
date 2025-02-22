FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# 创建必要的目录并设置权限
RUN mkdir -p uploads temp \
    && chmod -R 777 uploads temp \
    && chown -R nobody:nogroup uploads temp

# 切换到非root用户
USER nobody

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# 启动命令
CMD gunicorn --workers 2 --threads 4 --timeout 60 --bind 0.0.0.0:$PORT app:app 