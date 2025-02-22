FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8080

# 创建上传目录
RUN mkdir -p uploads temp

# 设置权限
RUN chmod -R 777 uploads temp

# 启动命令
CMD gunicorn --bind 0.0.0.0:$PORT app:app 