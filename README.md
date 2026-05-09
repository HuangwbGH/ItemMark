# ItemMark

ItemMark 是统一的物品标签打印与扫码查询系统。项目把旧的 `material-label-system` 和 `wupingPMC` 整合成一个 Docker 项目，在同一个域名下按模块区分标签打印、二维码内容和扫码后的查询页面。

默认对外域名：

```text
https://code.zestrade.com
```

应用服务端口使用非常用端口，避免和现有服务冲突：

```text
WEB_PORT=18089
HOST_WEB_PORT=18089
```

## 目录

- [功能说明](#功能说明)
  - [对外物料信息模块](#对外物料信息模块)
  - [武平模块](#武平模块)
- [目录结构](#目录结构)
- [使用说明](#使用说明)
  - [本地启动](#本地启动)
  - [常用入口](#常用入口)
  - [打印标签](#打印标签)
  - [手机扫码](#手机扫码)
  - [同步管理](#同步管理)
- [配置说明](#配置说明)
  - [全局配置](#全局配置)
  - [模块配置](#模块配置)
  - [标签模板配置](#标签模板配置)
- [API 说明](#api-说明)
- [部署说明](#部署说明)
  - [Linux Docker 部署](#linux-docker-部署)
  - [Nginx 配置](#nginx-配置)
- [验证命令](#验证命令)
- [注意事项](#注意事项)

## 功能说明

### 对外物料信息模块

模块标识：`material-info`

用途：

- 兼容旧项目 `material-label-system`。
- 打印对外物料信息标签。
- 手机扫码后显示物料基础信息。
- 保留旧二维码路径 `/material/{code}`，避免已打印标签失效。

默认账套：

```text
UFDATA_104_2018
```

主要页面：

```text
/material-info/batch              批量打印选择页
/material-info/print/{code}       单张标签打印
/material-info/batch/print        批量标签打印
/material-info/qr/{code}          模块二维码图片
/material-info/material/{code}    新模块扫码详情页
/material/{code}                  旧二维码兼容扫码详情页
```

兼容旧入口：

```text
/batch
/print/{code}
/batch/print?codes=...
/qr/{code}
```

### 武平模块

模块标识：`wuping`

用途：

- 兼容旧项目 `wupingPMC`。
- 打印仓库货架标签。
- 手机扫码后查询物料基础信息、当前结存、近一年出入库汇总和流水。

默认账套：

```text
UFDATA_105_2019
```

主要页面：

```text
/wuping/batch                    批量打印选择页
/wuping/print/{code}             单张标签打印
/wuping/batch/print              批量标签打印
/wuping/qr/{code}                模块二维码图片
/wuping/material/{code}          库存台账扫码详情页
```

## 目录结构

```text
ItemMark/
├── .env
├── .env.example
├── docker-compose.yml
├── README.md
├── certs/
│   └── code.zestrade.com/
├── config/
│   ├── nginx.conf
│   ├── modules/
│   │   ├── material-info.env
│   │   └── wuping.env
│   └── templates/
│       ├── material-info/label_config.xlsx
│       └── wuping/label_config.xlsx
├── data/
│   ├── admin/
│   ├── material-info/
│   ├── wuping/
│   └── legacy/
├── docs/
├── logs/
├── scripts/
├── sync/
├── tools/
└── web/
```

所有运行配置路径使用相对路径，例如：

```text
./data/material-info/itemmark.db
./data/wuping/itemmark.db
./config/templates/material-info/label_config.xlsx
./certs/code.zestrade.com/code.zestrade.com.key
```

## 使用说明

### 本地启动

```bash
bash scripts/start-dev.sh
```

启动后访问：

```text
http://127.0.0.1:18089/
```

停止：

```bash
bash scripts/stop-dev.sh
```

查看本地日志：

```bash
tail -f logs/dev-server.log
```

### 常用入口

```text
http://127.0.0.1:18089/                         首页
http://127.0.0.1:18089/admin/sync               同步管理
http://127.0.0.1:18089/material-info/batch      对外物料信息批量打印
http://127.0.0.1:18089/batch                    对外物料信息旧入口
http://127.0.0.1:18089/wuping/batch             武平批量打印
```

### 打印标签

1. 打开对应模块的批量打印页。
2. 搜索物料编码、名称、布卡号、规格、颜色等关键词。
3. 勾选需要打印的物料。
4. 点击“打印选中标签”。
5. 浏览器打开批量打印页后执行打印。

### 手机扫码

对外物料信息模块二维码内容：

```text
https://code.zestrade.com/material/{material_code}
```

武平模块二维码内容：

```text
https://code.zestrade.com/wuping/material/{material_code}
```

两个模块扫码后的页面不同：

- `/material/{code}`：物料基础信息。
- `/wuping/material/{code}`：库存台账。

### 同步管理

页面：

```text
/admin/sync
```

能力：

- 查看模块配置。
- 查看最近同步记录。
- 手动触发某个模块增量同步。
- 必要时手动触发全量同步。
- 通过勾选固定时间或选择固定频率来修改同步计划。

同步模式：

- 固定时间：页面直接勾选每天同步时间，例如 `08:00`、`10:00`、`14:00`、`18:00`。
- 固定频率：页面直接选择每 15 分钟、30 分钟、1 小时、2 小时等。

同步范围：

- 自动同步默认使用增量同步，避免每次全量抽取。
- 页面“增量同步”按钮只抽取最近一次成功同步后可能变更的物料。
- 首次没有历史成功同步记录时，增量同步会自动执行一次全量初始化。
- 页面“全量同步”按钮用于配置变更或必要的人工修复。
- 如果目标 U8 账套缺少可用于增量判断的物料修改时间字段，系统会自动降级为全量同步，并在同步结果中记录原因。

首版不做应用登录，也暂不做 Nginx IP 白名单。

## 配置说明

### 全局配置

文件：

```text
.env
```

示例：

```ini
APP_NAME=ItemMark
BASE_DOMAIN=https://code.zestrade.com
ADMIN_DB_PATH=./data/admin/itemmark_admin.db
WEB_HOST=0.0.0.0
WEB_PORT=18089
HOST_WEB_PORT=18089
LOG_LEVEL=INFO
LOG_FILE=./logs/itemmark.log
```

说明：

| 配置项 | 说明 |
|---|---|
| `BASE_DOMAIN` | 对外域名 |
| `ADMIN_DB_PATH` | 同步记录管理库 |
| `WEB_PORT` | Web 容器监听端口 |
| `HOST_WEB_PORT` | 宿主机映射端口 |
| `LOG_LEVEL` | 日志级别 |

### 模块配置

文件：

```text
config/modules/material-info.env
config/modules/wuping.env
```

对外物料信息模块：

```ini
MODULE_KEY=material-info
MODULE_NAME=对外物料信息
BASE_PATH=/material-info
QR_BASE_URL=https://code.zestrade.com
SQLITE_PATH=./data/material-info/itemmark.db
U8_HOST=192.168.1.135
U8_PORT=1433
U8_DATABASE=UFDATA_104_2018
U8_USER=testreadonly
U8_PASSWORD=...
TEMPLATE_PATH=./config/templates/material-info/label_config.xlsx
DETAIL_TYPE=material_info
LEDGER_ENABLED=false
SYNC_ENABLED=true
SYNC_MODE=cron
SYNC_CRON=0 8,10,14,18 * * *
SYNC_INTERVAL_MINUTES=60
```

武平模块：

```ini
MODULE_KEY=wuping
MODULE_NAME=武平
BASE_PATH=/wuping
QR_BASE_URL=https://code.zestrade.com/wuping
SQLITE_PATH=./data/wuping/itemmark.db
U8_HOST=192.168.1.135
U8_PORT=1433
U8_DATABASE=UFDATA_105_2019
U8_USER=testreadonly
U8_PASSWORD=...
TEMPLATE_PATH=./config/templates/wuping/label_config.xlsx
DETAIL_TYPE=ledger
LEDGER_ENABLED=true
SYNC_ENABLED=true
SYNC_MODE=cron
SYNC_CRON=0 8,10,14,18 * * *
SYNC_INTERVAL_MINUTES=60
```

关键配置：

| 配置项 | 说明 |
|---|---|
| `MODULE_KEY` | 模块标识 |
| `BASE_PATH` | 模块页面路径前缀 |
| `QR_BASE_URL` | 打入二维码的 URL 前缀 |
| `SQLITE_PATH` | 当前模块 SQLite 数据库 |
| `U8_DATABASE` | 当前模块使用的 U8 账套 |
| `TEMPLATE_PATH` | 当前模块标签模板 |
| `DETAIL_TYPE` | `material_info` 或 `ledger` |
| `LEDGER_ENABLED` | 是否启用库存台账查询 |
| `SYNC_MODE` | `cron` 或 `interval` |
| `SYNC_CRON` | 定时同步表达式 |
| `SYNC_INTERVAL_MINUTES` | 固定频率同步间隔分钟 |

### 标签模板配置

文件：

```text
config/templates/material-info/label_config.xlsx
config/templates/wuping/label_config.xlsx
```

标签模板控制：

- 标签宽度。
- 标签最小高度。
- 内边距。
- 名称字号。
- 字段字号。
- 二维码大小。
- 每行标签数。
- 每页标签数。
- 显示字段和显示顺序。
- 标签底部是否显示。
- 标签底部字号。
- 标签底部左侧内容。
- 标签底部右侧内容。

底部内容支持占位符：

| 占位符 | 说明 |
|---|---|
| `{material_code}` | 物料编码 |
| `{material_name}` | 物料名称 |
| `{cloth_card_no}` | 布卡号 |
| `{specification}` | 规格型号 |
| `{color_desc}` | 颜色 |
| `{com_unit_name}` | 单位 |
| `{sync_updated_at}` | 数据同步时间 |
| `{print_time}` | 打印页面生成时间 |

示例：

```text
底部左侧内容：{material_code}
底部右侧内容：打印时间 {print_time}
```

生成或重置模板：

```bash
python3 tools/create_label_config.py --module material-info
python3 tools/create_label_config.py --module wuping
```

注意：重置会覆盖对应模块模板。

## API 说明

健康检查：

```text
GET /api/health
```

模块列表：

```text
GET /api/modules
```

模块物料查询：

```text
GET  /api/{module}/materials?keyword=&limit=&offset=
GET  /api/{module}/material/{code}
POST /api/{module}/materials/by-codes
```

标签配置：

```text
GET /api/{module}/label-config
```

武平台账：

```text
GET /api/wuping/material/{code}/ledger?start_date=&end_date=
```

同步：

```text
GET  /api/{module}/sync/status
POST /api/{module}/sync/run
GET  /api/{module}/sync/config
PUT  /api/{module}/sync/config
```

兼容旧项目 1：

```text
GET /api/material/{code}
GET /api/materials
```

## 部署说明

### Linux Docker 部署

1. 上传项目到服务器。
2. 确认 `.env`、`config/modules/*.env` 中的 U8 地址、账套、账号、密码正确。
3. 确认 `certs/code.zestrade.com/` 中证书文件存在。
4. 构建并启动：

```bash
docker-compose up -d --build
```

5. 查看容器：

```bash
docker-compose ps
```

6. 查看日志：

```bash
docker-compose logs -f web
docker-compose logs -f sync
```

7. 验证服务：

```bash
curl http://127.0.0.1:18089/api/health
```

### Nginx 配置

示例文件：

```text
config/nginx.conf
```

核心代理：

```nginx
location / {
    proxy_pass http://127.0.0.1:18089;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 60s;
}
```

正式部署后访问：

```text
https://code.zestrade.com/
https://code.zestrade.com/material/{code}
https://code.zestrade.com/wuping/material/{code}
```

## 验证命令

```bash
python3 -m py_compile sync/*.py web/*.py web/routers/*.py web/services/*.py web/db/*.py
docker-compose config
curl http://127.0.0.1:18089/api/health
```

## 注意事项

- 首次正式运行应通过 `/admin/sync` 重新同步数据。
- 旧数据库已复制到 `data/legacy/` 作为参考和回滚资料。
- 已打印出去的二维码不会随配置自动变化；更改 `QR_BASE_URL` 后需要重新同步并重新打印标签。
- 后台首版无登录保护，部署时请按实际网络环境控制访问范围。
- 不要把运行路径改成绝对路径；配置中保持 `./data/...`、`./config/...` 这类相对路径。
