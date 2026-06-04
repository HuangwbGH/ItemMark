# ItemMark 部署说明

状态：当前部署文档

## 目录

- [1. 部署目标](#1-部署目标)
- [2. Docker 服务](#2-docker-服务)
- [3. Linux Docker 部署](#3-linux-docker-部署)
- [4. Nginx 反向代理](#4-nginx-反向代理)
- [5. 常用运维命令](#5-常用运维命令)
- [6. 部署注意事项](#6-部署注意事项)

## 1. 部署目标

ItemMark 需要支持 Linux OS 上通过 Docker 部署运行，对外统一使用：

```text
https://code.zestrade.com
```

应用服务端口使用非常用端口：

```text
18089
```

## 2. Docker 服务

`docker-compose.yml` 定义两个服务：

| 服务 | 容器名 | 说明 |
|---|---|---|
| `web` | `itemmark-web` | FastAPI Web 页面和 API |
| `sync` | `itemmark-sync` | 模块数据同步任务 |

挂载目录：

```text
./data
./config
./certs
./logs
```

## 3. Linux Docker 部署

1. 上传项目到服务器。
2. 确认 `.env` 中全局配置正确。
3. 确认 `config/modules/*.env` 中模块 U8 配置正确。
4. 确认 `certs/code.zestrade.com/` 中证书文件存在。
5. 构建并启动：

```bash
docker-compose up -d --build
```

6. 查看服务：

```bash
docker-compose ps
```

7. 查看日志：

```bash
docker-compose logs -f web
docker-compose logs -f sync
```

8. 健康检查：

```bash
curl http://127.0.0.1:18089/api/health
```

## 4. Nginx 反向代理

配置文件：

```text
config/nginx.conf
```

核心代理目标：

```text
http://127.0.0.1:18089
```

主要访问入口：

```text
https://code.zestrade.com/
https://code.zestrade.com/admin/sync
https://code.zestrade.com/material/{code}
https://code.zestrade.com/material-info/batch
https://code.zestrade.com/wuping/batch
https://code.zestrade.com/wuping/material/{code}
```

## 5. 常用运维命令

本地开发启动：

```bash
bash scripts/start-dev.sh
```

本地开发停止：

```bash
bash scripts/stop-dev.sh
```

Docker 配置检查：

```bash
docker-compose config
```

## 6. 部署注意事项

- 首次正式运行应通过 `/admin/sync` 重新同步数据。
- 旧二维码 `/material/{code}` 必须继续指向对外物料信息模块。
- 后台首版无登录保护，生产环境需要通过网络边界控制访问风险。
- 证书私钥不得写入文档或日志。
- 配置路径保持相对路径，不写入本机绝对路径。
