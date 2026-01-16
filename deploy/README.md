# 部署指南

你的服务器: `59.110.55.185` (Ubuntu 22.04)

## 方式一：Docker 部署（推荐，你服务器已装 Docker）

```bash
# 1. 上传项目到服务器
scp -r . root@59.110.55.185:/opt/pixel-art

# 2. SSH 登录服务器
ssh root@59.110.55.185

# 3. 构建并运行
cd /opt/pixel-art
docker build -t pixel-art -f deploy/Dockerfile .
docker run -d -p 7860:7860 --name pixel-art --restart unless-stopped pixel-art

# 4. 访问
# http://59.110.55.185:7860
```

## 方式二：直接部署

```bash
# 1. 上传项目到服务器
scp -r . root@59.110.55.185:/opt/pixel-art

# 2. SSH 登录服务器
ssh root@59.110.55.185

# 3. 进入项目目录并运行部署脚本
cd /opt/pixel-art
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

## 方式二：Docker 部署（推荐）

```bash
# 1. 构建镜像
docker build -t pixel-art -f deploy/Dockerfile .

# 2. 运行容器
docker run -d -p 7860:7860 --name pixel-art --restart unless-stopped pixel-art
```

## 方式三：Systemd 服务（后台运行）

```bash
# 1. 先用方式一安装依赖

# 2. 复制服务文件
sudo cp deploy/pixel-art.service /etc/systemd/system/

# 3. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable pixel-art
sudo systemctl start pixel-art

# 查看状态
sudo systemctl status pixel-art
```

## 配置 Nginx 反向代理（可选）

```bash
# 1. 安装 Nginx
sudo apt install nginx

# 2. 复制配置
sudo cp deploy/nginx.conf /etc/nginx/sites-available/pixel-art
sudo ln -s /etc/nginx/sites-available/pixel-art /etc/nginx/sites-enabled/

# 3. 修改域名
sudo nano /etc/nginx/sites-available/pixel-art

# 4. 重启 Nginx
sudo nginx -t
sudo systemctl restart nginx
```

## 访问

- 直接访问: `http://服务器IP:7860`
- 通过 Nginx: `http://你的域名`
