# ItemMark 项目 Nginx 配置说明

## 一、Nginx 在项目中的作用

ItemMark 是统一运行在 Docker 容器内的 Web 应用，内部服务端口为 **`18089`**。Nginx 作为反向代理层，承担以下核心职责：

| 作用 | 说明 |
|---|---|
| **反向代理** | 将外网对 80/443/34433 端口的请求转发给本机 `127.0.0.1:18089`（Docker 容器） |
| **SSL/TLS 终止** | Nginx 处理 HTTPS 加密解密（证书卸载），后端容器只需跑纯 HTTP |
| **HTTP 自动跳转** | 80 端口的 HTTP 请求自动 301 跳转到 HTTPS，避免明文传输 |
| **统一入口** | 对外提供标准域名+端口访问，整合 material-info、wuping 等多个模块 |
| **证书管理** | 集中存放和管理 HTTPS 证书，业务代码无需关心证书逻辑 |

```
外网用户 (手机/电脑)
    │
    ▼
https://code.zestrade.com:34433/
    │
    ▼
路由器 443/34433 端口映射
    │
    ▼
Nginx (0.0.0.0:443 / 0.0.0.0:34433)
    │  SSL 解密 + Host 头透传
    ▼
Docker 容器 (127.0.0.1:18089)
    │
    ▼
ItemMark Web 服务
```

---

## 二、工作原理

### 2.1 为什么需要 Nginx？

ItemMark 的 Docker 容器只把 `18089` 映射到了宿主机：

```yaml
# docker-compose.yml
services:
  web:
    ports:
      - "18089:18089"
```

如果直接让外网访问 `http://xxx:18089`，存在三个问题：
1. **端口不标准** — 用户需要记忆非常用端口，容易出错
2. **无 HTTPS** — 明文传输，手机浏览器/微信会拦截或提示"不安全"
3. **无自动跳转** — 用户可能误用 HTTP，导致二维码链接失效或中间人攻击

Nginx 解决了以上所有问题：对外暴露标准的 **80/443** 端口，提供 **HTTPS** 加密，并自动把 HTTP 跳转到 HTTPS。

### 2.2 请求完整流向

以手机扫码访问 `https://code.zestrade.com:34433/material/2101010045` 为例：

| 步骤 | 处理方 | 动作 |
|---|---|---|
| 1 | 手机浏览器 | DNS 解析 `code.zestrade.com` → 公网 IP |
| 2 | 路由器 | NAT 端口映射：公网 IP:34433 → 192.168.1.14:34433 |
| 3 | Nginx | 接收 HTTPS 请求，SSL 握手，验证证书 |
| 4 | Nginx | 解密后把请求转发到 `http://127.0.0.1:18089/material/2101010045` |
| 5 | Nginx | 将后端返回的响应重新加密，回传给手机 |

### 2.3 关键请求头透传

Nginx 在反向代理时会向后端传递以下头部，确保业务逻辑正确：

```nginx
proxy_set_header Host $host;                    # 保留原始域名
proxy_set_header X-Real-IP $remote_addr;        # 真实客户端 IP
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # 代理链 IP
proxy_set_header X-Forwarded-Proto $scheme;     # 原始协议 https
```

ItemMark 后端通过这些头部生成正确的二维码 URL、判断访问协议等。

---

## 三、配置文件说明

### 3.1 实际生效的系统配置

**路径：** `/etc/nginx/sites-available/code.zestrade.com`

**软链接：** `/etc/nginx/sites-enabled/code.zestrade.com → /etc/nginx/sites-available/code.zestrade.com`

> ⚠️ **注意：** Nginx 启动时读取的是 `/etc/nginx/sites-enabled/` 下的文件，修改项目目录 `/root/ItemMark/config/nginx.conf` 不会自动生效，必须同步到系统配置并执行 `nginx -s reload`。

### 3.2 配置内容详解

```nginx
# HTTP 入口：强制跳转到 HTTPS
server {
    listen 80;
    server_name code.zestrade.com;
    return 301 https://$host$request_uri;
}

# HTTPS 入口：处理所有业务请求
server {
    listen 443 ssl;
    listen 34433 ssl;       # 非标准端口，用于外网备案后访问
    server_name code.zestrade.com;

    # SSL 证书（必须使用绝对路径）
    ssl_certificate     /root/ItemMark/certs/code.zestrade.com/code.zestrade.com.crt;
    ssl_certificate_key /root/ItemMark/certs/code.zestrade.com/code.zestrade.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    # 反向代理到 ItemMark Docker 容器
    location / {
        proxy_pass http://127.0.0.1:18089;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

### 3.3 项目目录下的参考配置

**路径：** `/root/ItemMark/config/nginx.conf`

这个文件是项目自带的**参考模板**，供部署时参考。其中的证书路径写的是相对路径 `./certs/...`，直接用于系统 Nginx 时会因路径解析错误导致启动失败。

**正确做法：** 将项目模板的内容复制到 `/etc/nginx/sites-available/code.zestrade.com`，并把证书路径改为**绝对路径**。

---

## 四、常用操作命令

```bash
# 测试配置语法是否正确（修改后必做）
nginx -t

# 平滑重载配置（不中断现有连接）
nginx -s reload

# 查看 Nginx 运行状态
systemctl status nginx

# 重启 Nginx 服务（配置错误无法 reload 时使用）
systemctl restart nginx

# 查看 Nginx 访问日志
tail -f /var/log/nginx/access.log

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log
```

---

## 五、注意事项与常见问题

### 5.1 修改配置后必须 reload

Nginx 只有在 `start` 或 `reload` 时才会重新读取配置文件。修改 `/etc/nginx/sites-available/code.zestrade.com` 后，**必须执行：**

```bash
nginx -t && nginx -s reload
```

### 5.2 证书路径必须用绝对路径

系统 Nginx 的工作目录通常是 `/etc/nginx` 或 `/`，相对路径 `./certs/xxx` 会解析到错误位置，导致：

```
nginx: [emerg] BIO_new_file("./certs/...") failed (SSL: error:02001002:system library:fopen:No such file or directory)
```

**正确写法：**
```nginx
ssl_certificate /root/ItemMark/certs/code.zestrade.com/code.zestrade.com.crt;
```

### 5.3 防火墙必须放行端口

UFW 或 iptables 需要显式允许 80、443、34433：

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 34433/tcp
```

### 5.4 路由器端口映射

外网访问需要路由器做 **NAT 端口映射（虚拟服务器）**：

| 外部端口 | 内部 IP | 内部端口 | 协议 |
|---|---|---|---|
| 80 | 192.168.1.14 | 80 | TCP |
| 443 | 192.168.1.14 | 443 | TCP |
| 34433 | 192.168.1.14 | 34433 | TCP |

> 如果之前成功过后来不行，优先检查路由器映射是否因重启丢失。

### 5.5 二维码 URL 端口一致性

ItemMark 生成的二维码内容基于 `QR_BASE_URL`。如果 Nginx 监听的是 **34433**，则 `.env` 和模块配置中的 `QR_BASE_URL` 必须带上该端口：

```ini
# config/modules/material-info.env
QR_BASE_URL=https://code.zestrade.com:34433

# config/modules/wuping.env
QR_BASE_URL=https://code.zestrade.com:34433/wuping
```

修改后需要重启 Docker 容器才能生效：

```bash
cd /root/ItemMark && docker compose restart
```

### 5.6 域名解析检查清单

外网无法访问时，按以下顺序排查：

1. **域名解析** — `dig code.zestrade.com` 是否指向正确公网 IP？
2. **路由器映射** — 端口转发是否配置并生效？
3. **本机防火墙** — `ufw status` 是否放行了对应端口？
4. **Nginx 监听** — `ss -tlnp | grep ':443'` 是否显示 `0.0.0.0:443`？
5. **后端服务** — `curl http://127.0.0.1:18089/api/health` 是否返回正常？
6. **Nginx 配置** — `nginx -t` 是否通过？

---

## 六、总结

Nginx 在 ItemMark 项目中是**外网与 Docker 容器之间的网关**，负责：

- 提供标准 HTTPS 入口（域名 + 443/34433）
- SSL 加密卸载
- HTTP 自动跳转
- 请求头透传

**配置核心原则：** 系统配置用绝对路径、改完必 reload、防火墙和路由器要放行、二维码 URL 端口与 Nginx 监听端口保持一致。
