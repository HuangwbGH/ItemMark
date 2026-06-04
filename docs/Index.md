# ItemMark 文档索引

状态：当前文档入口

## 目录

- [1. 文档地图](#1-文档地图)
- [2. 权威来源](#2-权威来源)
- [3. 维护规则](#3-维护规则)
- [4. 待补目录](#4-待补目录)

## 1. 文档地图

| 文档 | 用途 |
|---|---|
| `../README.md` | 项目入口、运行方式、常用入口、API 和部署摘要 |
| `../AGENTS.md` | AI 协作、开发、验证、文档同步规则 |
| `../PRD.md` | 根目录 PRD 入口 |
| `01-项目整合PRD.md` | 产品需求主文档 |
| `02-程序设计实现方案.md` | 技术设计主文档 |
| `03-项目阅读与整合决策.md` | 旧项目阅读结论和整合决策 |
| `20260513库存台账查询变更.md` | 武平账套库存台账 SQL 参考 |
| `Config.md` | 配置项说明 |
| `DatabaseSchema.md` | 数据库结构说明 |
| `Deployment.md` | Docker、Nginx 和 Linux 部署说明 |
| `ProcessTodo.md` | 当前任务、待办、阻塞项、用户需提供内容 |
| `TestReport.md` | 测试记录、验证命令和遗留风险 |

## 2. 权威来源

- 产品范围以 `01-项目整合PRD.md` 为准。
- 技术方案以 `02-程序设计实现方案.md` 为准。
- 配置项以 `Config.md` 和实际 `config/modules/*.env` 为准。
- 部署方式以 `Deployment.md`、`docker-compose.yml` 和 `config/nginx.conf` 为准。
- 数据库结构以 `DatabaseSchema.md` 和 `web/db/`、`sync/db_sqlite.py` 为准。
- 测试结论以 `TestReport.md` 为准。

## 3. 维护规则

- 所有文档必须保留目录。
- 路径示例使用相对路径。
- 不记录真实密钥、真实 Token、真实密码或生产隐私数据。
- 内容未确认时标记“待确认”。
- 内容废弃时标记“已废弃”，并说明替代文档或废弃原因。

## 4. 待补目录

以下目录是规范推荐目录，当前没有独立内容时可以暂不创建；新增对应事项时再补齐：

```text
docs/Milestones/
docs/Specs/
docs/ProductIterations/
docs/TechnicalValidation/
docs/Design/
docs/References/
```
