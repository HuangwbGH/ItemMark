# ItemMark 测试报告

状态：当前验证记录

## 目录

- [1. 测试范围](#1-测试范围)
- [2. 最近验证](#2-最近验证)
- [3. 标准验证命令](#3-标准验证命令)
- [4. 功能验收清单](#4-功能验收清单)
- [5. 遗留风险](#5-遗留风险)

## 1. 测试范围

本文记录 ItemMark 的代码检查、Docker 配置检查和功能验收结果。

## 2. 最近验证

日期：2026-06-04

变更范围：`material-info` 模块新增多打印模板选择和辅料双联模板。

已执行检查：

```bash
python3 -m py_compile sync/*.py web/*.py web/routers/*.py web/services/*.py web/db/*.py
python3 -m py_compile tools/create_label_config.py
docker-compose config
bash scripts/start-dev.sh
curl http://127.0.0.1:18089/api/health
```

模板读取验证：

```text
material-info 可列出 default 标准模板和 accessory_split_2 辅料双联模板。
accessory_split_2 读取结果：模板名称=辅料双联模板，布局类型=split_2，显示字段=material_name、material_code、color_desc。
```

页面渲染验证：

```text
GET /material-info/batch -> 200，页面包含模板选择框和辅料双联模板。
GET /material-info/print/1 -> 200，页面包含模板选择框和标准模板。
GET /material-info/print/1?template=accessory_split_2 -> 200，页面使用 split-card 布局。
GET /material-info/batch/print?codes=1&template=accessory_split_2 -> 200，页面使用 split-card 布局并显示辅料双联模板。
GET /material-info/batch/print?codes=1&template=bad/name -> 404，非法模板 key 被拒绝。
```

辅料双联布局更新验证：

```text
split_2 布局使用 grid-template-rows: 1fr 1fr。
第二个信息区使用 border-top 分隔，表示上下双联。
```

本地服务验证：

```text
GET http://127.0.0.1:18089/api/health -> {"code":0,"service":"ItemMark"}
GET http://127.0.0.1:18089/material-info/batch -> 页面包含 template-select、accessory_split_2、辅料双联模板。
GET http://127.0.0.1:18089/material-info/print/1?template=accessory_split_2 -> 页面包含 template-select、selected、split-card。
GET http://127.0.0.1:18089/material-info/print/1?template=accessory_split_2 -> 页面包含 grid-template-rows: 1fr 1fr 和 border-top: 1px dashed #999。
GET http://127.0.0.1:18089/material-info/batch/print?codes=1&template=accessory_split_2 -> 页面包含 grid-template-rows: 1fr 1fr 和 border-top: 1px dashed #999。
GET http://127.0.0.1:18089/material-info/print/1?template=accessory_split_2 -> 紧凑样式生效，物料名称字段标题出现次数为 0。
GET http://127.0.0.1:18089/material-info/batch/print?codes=1&template=accessory_split_2 -> 紧凑样式生效，物料名称字段标题出现次数为 0。
```

结果：通过。

说明：本地开发服务已通过 `scripts/start-dev.sh` 启动。

## 3. 标准验证命令

语法检查：

```bash
python3 -m py_compile sync/*.py web/*.py web/routers/*.py web/services/*.py web/db/*.py
```

Docker 配置检查：

```bash
docker-compose config
```

健康检查：

```bash
curl http://127.0.0.1:18089/api/health
```

## 4. 功能验收清单

- [ ] 首页 `/` 可访问。
- [ ] 同步管理 `/admin/sync` 可访问。
- [ ] 对外物料信息批量打印 `/material-info/batch` 可访问。
- [ ] 旧入口 `/batch` 可访问。
- [ ] 武平批量打印 `/wuping/batch` 可访问。
- [ ] 旧二维码 `/material/{code}` 返回对外物料信息。
- [ ] 武平二维码 `/wuping/material/{code}` 返回库存台账页。
- [ ] `/api/health` 返回健康状态。

## 5. 遗留风险

- 后台首版无登录保护，生产环境需依赖网络边界控制。
- U8 连接和真实台账结果需要在可访问 U8 的环境中验证。
- 已打印二维码不随配置自动变更，修改二维码前缀后需要重新打印标签。
