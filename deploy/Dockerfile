FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# Gradio 默认端口
EXPOSE 7860

# 启动应用
CMD ["python", "app.py"]
