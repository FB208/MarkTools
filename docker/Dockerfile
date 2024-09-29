# 使用官方的Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目的依赖文件
COPY requirements.txt requirements.txt

# 安装项目依赖
# 改动量比较大，推进使用无缓存模式RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 复制项目的所有文件到工作目录
COPY . .

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 暴露应用运行的端口
EXPOSE 5000

# 启动Flask应用
# CMD ["flask", "run"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "3000", "--workers", "3", "--threads", "3", "app:app"]