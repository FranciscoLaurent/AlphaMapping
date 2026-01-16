# AlphaMapping Docker 部署指南

本文档介绍如何使用 Docker 部署 AlphaMapping 平台。

## 📋 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间

## 🚀 快速启动

### 1. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 复制示例配置
cp backend/.env.example .env

# 编辑配置
nano .env  # 或使用任意编辑器
```

必填配置项：
```env
FOFA_EMAIL=your_fofa_email
FOFA_KEY=your_fofa_api_key
ZOOMEYE_KEY=your_zoomeye_api_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

### 2. 构建并启动

```bash
# 构建镜像并启动服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 访问服务

- **前端界面**: http://localhost
- **API 文档**: http://localhost:8000/docs
- **API 端点**: http://localhost:8000

## 📁 数据持久化

容器数据存储在 `./data` 目录：

```
data/
├── alpha_mapping.db    # SQLite 数据库
└── reports/           # 生成的报告文件
```

> ⚠️ **重要**: 请定期备份 `data/` 目录。

## 🔧 常用命令

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重建并启动（代码更新后）
docker-compose up -d --build

# 查看容器日志
docker-compose logs backend
docker-compose logs frontend

# 进入容器调试
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🌐 生产环境配置

### 使用自定义域名

修改 `docker/nginx.conf`：
```nginx
server_name your-domain.com;
```

### 启用 HTTPS

建议使用 Nginx 反向代理或 Traefik 处理 SSL 证书。

示例 Traefik 配置（在 docker-compose.yml 中添加）：
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.alphamapping.rule=Host(`your-domain.com`)"
  - "traefik.http.routers.alphamapping.entrypoints=websecure"
  - "traefik.http.routers.alphamapping.tls.certresolver=letsencrypt"
```

### 资源限制

在 `docker-compose.yml` 中添加：
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## 🔍 故障排除

### 容器无法启动

检查日志：
```bash
docker-compose logs backend
```

常见问题：
1. **端口冲突**: 确保 80 和 8000 端口未被占用
2. **权限问题**: 确保 `data/` 目录可写
3. **配置错误**: 检查 `.env` 文件格式

### API 请求失败

1. 检查后端健康状态：
   ```bash
   curl http://localhost:8000/
   ```

2. 检查 Nginx 代理：
   ```bash
   docker-compose logs frontend
   ```

### 数据库问题

重置数据库（⚠️ 会丢失数据）：
```bash
docker-compose down
rm -rf data/alpha_mapping.db
docker-compose up -d
```

## 📊 监控

### 健康检查

服务内置健康检查，可通过以下命令查看：
```bash
docker-compose ps
```

### 资源使用

```bash
docker stats alphamapping-backend alphamapping-frontend
```

## 🔄 更新升级

```bash
# 拉取最新代码
git pull

# 重建镜像
docker-compose build --no-cache

# 重启服务
docker-compose up -d
```

---

如有问题，请提交 Issue 或联系维护团队。
