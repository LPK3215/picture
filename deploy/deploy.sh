#!/bin/bash
# 像素画生成器 - 服务器部署脚本

set -e

echo "=== 像素画生成器部署脚本 ==="

# 1. 更新系统并安装依赖
echo "[1/4] 安装系统依赖..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 2. 创建虚拟环境
echo "[2/4] 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 3. 安装 Python 依赖
echo "[3/4] 安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. 启动服务
echo "[4/4] 启动服务..."
echo "应用将在 http://0.0.0.0:7860 运行"
python app.py
