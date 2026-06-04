# ItemMark 配置说明

状态：当前配置文档

## 目录

- [1. 配置来源](#1-配置来源)
- [2. 全局配置](#2-全局配置)
- [3. 模块配置](#3-模块配置)
- [4. 标签模板配置](#4-标签模板配置)
- [5. 路径和密钥规则](#5-路径和密钥规则)

## 1. 配置来源

配置读取入口：

```text
.env
config/modules/material-info.env
config/modules/wuping.env
config/templates/material-info/label_config.xlsx
config/templates/wuping/label_config.xlsx
```

模块配置优先级：

1. 管理库 `data/admin/itemmark_admin.db` 中保存的配置。
2. `config/modules/{module}.env`。
3. 代码默认值。

## 2. 全局配置

示例文件：

```text
.env.example
```

主要配置：

| 配置项 | 说明 | 示例 |
|---|---|---|
| `APP_NAME` | 应用名称 | `ItemMark` |
| `BASE_DOMAIN` | 对外域名 | `https://code.zestrade.com` |
| `ADMIN_DB_PATH` | 管理库路径 | `./data/admin/itemmark_admin.db` |
| `WEB_HOST` | Web 监听地址 | `0.0.0.0` |
| `WEB_PORT` | 容器内 Web 端口 | `18089` |
| `HOST_WEB_PORT` | 宿主机映射端口 | `18089` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `LOG_FILE` | 日志文件 | `./logs/itemmark.log` |

## 3. 模块配置

模块配置文件：

```text
config/modules/material-info.env
config/modules/wuping.env
```

主要配置：

| 配置项 | 说明 |
|---|---|
| `MODULE_KEY` | 模块标识 |
| `MODULE_NAME` | 模块名称 |
| `BASE_PATH` | 模块页面路径前缀 |
| `QR_BASE_URL` | 二维码 URL 前缀 |
| `SQLITE_PATH` | 模块 SQLite 路径 |
| `U8_HOST` | U8 数据库地址 |
| `U8_PORT` | U8 数据库端口 |
| `U8_DATABASE` | U8 账套数据库名 |
| `U8_USER` | U8 用户 |
| `U8_PASSWORD` | U8 密码 |
| `TEMPLATE_PATH` | 标签模板路径 |
| `DETAIL_TYPE` | 扫码详情类型，`material_info` 或 `ledger` |
| `LEDGER_ENABLED` | 是否启用库存台账 |
| `SYNC_ENABLED` | 是否启用自动同步 |
| `SYNC_MODE` | 同步模式，`cron` 或 `interval` |
| `SYNC_CRON` | 定时同步表达式 |
| `SYNC_INTERVAL_MINUTES` | 固定频率同步间隔 |

## 4. 标签模板配置

标签模板文件：

```text
config/templates/material-info/label_config.xlsx
config/templates/material-info/accessory_split_2.xlsx
config/templates/wuping/label_config.xlsx
```

模板控制：

- 模板名称。
- 布局类型：`standard` 或 `split_2`。
- 标签宽度、高度、内边距。
- 二维码大小。
- 每行标签数和每页标签数。
- 名称、字段、底部信息的字体和字号。
- 字段固定标题字号，例如辅料双联模板中的“物料编码”“颜色”。
- 显示字段、显示顺序和字段截断行数。
- 颜色字段最多行数。
- 字段固定标题列宽。
- 底部内容占位符。

`material-info` 模块支持多个打印模板：

- `label_config.xlsx` 是默认模板。
- 同目录下其他 `.xlsx` 文件会作为可选模板出现在批量打印页。
- `accessory_split_2.xlsx` 是辅料双联模板，在原打印纸大小内上下打印两个信息区，字段为物料名称、物料编码、颜色和二维码。
- 辅料双联模板的“颜色最多行数”默认值为 `4`，可在 Excel `配置` 工作表中调整；设置为 `0` 时不限制。
- 辅料双联模板的“字段标签字号”默认值为 `7`，用于控制“物料编码”“颜色”等固定标题大小。
- 辅料双联模板的“标签列宽”默认值为 `52`，用于控制固定标题列宽。

重置模板命令：

```bash
python3 tools/create_label_config.py --module material-info
python3 tools/create_label_config.py --module wuping
python3 tools/create_label_config.py --module material-info --template accessory-split-2
```

## 5. 路径和密钥规则

允许的路径形式：

```text
./data/admin/itemmark_admin.db
./data/material-info/itemmark.db
./data/wuping/itemmark.db
./config/templates/material-info/label_config.xlsx
./logs/itemmark.log
```

禁止在文档、配置示例或代码中写入本机绝对路径。真实密码、证书私钥、Token 不写入文档。
