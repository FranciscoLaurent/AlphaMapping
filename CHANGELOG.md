# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **ZoomEye 查询 `size` 参数失效**：此前 `size` 被完全忽略，单次请求无法控制返回数量。现已按 `size` 上限截断结果，并在需要时翻页累积。
- **FOFA 查询缺少 HTTP 错误处理**：补充非 200 状态码检查、网络异常捕获（`httpx.HTTPError`）、JSON 解析防护，并在非 200 时优先透出 API 返回的 `errmsg`。
- **服务层调试 `print` 改为 `logging`**：`fofa.py`、`agent.py` 中的 `print` 调试语句替换为 `logger.debug`，符合项目 Python 代码规范。
- **`test_services.py` 中 `OpenAI` mock 路径错误**：`patch('app.services.agent.OpenAI')` 修正为 `patch('openai.OpenAI')`，修复该测试的 setup error。
- **前端 XSS 漏洞**：所有 innerHTML 拼接点引入 escapeHtml/escapeAttr 转义；历史/报告 onclick 改为缓存索引引用；LLM 报告先转义再做 markdown 替换；高危资产从 Math.random() 改为敏感端口启发式统计。
- **CORS 凭证泄露**：`allow_credentials=True` + `origins=["*"]` 允许任意网站携带凭证发请求，改为 `allow_credentials=False`。
- **platform 字段无校验**：改用 `Literal['fofa', 'zoomeye']` 类型约束，阻止 LLM prompt 注入和静默 fallback。
- **错误信息泄露内部细节**：`str(e)` 直接返回客户端改为通用错误消息，详细信息仅写日志。
- **/stats 全表加载 OOM**：地理分布改用 SQL 查询过滤，不再 `Asset.all()` 加载全部资产到内存。
- **LLM 失败原样返回用户输入**：改为抛异常，避免烧外部平台 API 额度。
- **updateFilterOptions 未转义**：country/protocol 直接进 innerHTML，补充 escapeHtml/escapeAttr。
- **onclick 中 id 未校验**：asset.id/r.id 补充 Number.isSafeInteger 校验。
- **formatMarkdown 贪婪正则**：`(.*)` 改为 `(.*?)` 避免跨匹配吞并。

### Tests
- 为 FOFA / ZoomEye 平台查询新增单元测试：结果解析、`size` 参数传递与截断、HTTP 错误与 API 错误体抛异常。
- 在 `conftest.py` 补充 ZoomEye、FOFA 错误响应等 mock fixtures。

## [1.0.0] - 2026-01-16

### Added
- **Core Features**
  - Natural language to CSEQL query translation (NL2CSEQL)
  - Multi-platform asset aggregation (FOFA, ZoomEye)
  - Local SQLite database with intelligent caching
  - AI-powered security analysis reports

- **Dashboard**
  - Real-time situational awareness dashboard
  - Interactive ECharts visualizations (port distribution, protocol analysis, geo map)
  - Asset list with 5-column grid layout
  - Click-to-filter chart interaction

- **Data Management**
  - Asset data deduplication (IP:Port unique constraint)
  - Data export (CSV, Excel, JSON formats)
  - Asset filtering (keyword, country, protocol)
  - Clear history functionality

- **Scheduled Tasks**
  - APScheduler-based task scheduling
  - Cron expression support
  - Task CRUD API endpoints
  - Auto-load on application startup

- **Deployment**
  - Docker containerization support
  - docker-compose configuration
  - PowerShell automation scripts (run, stop, restart)
  - Nginx reverse proxy configuration

- **Testing**
  - pytest test framework
  - API endpoint tests
  - Service layer tests
  - Model tests

- **Documentation**
  - README.md (Chinese)
  - README.en.md (English)
  - README.Docker.md
  - CONTRIBUTING.md
  - SECURITY.md

### Security
- Environment variable based configuration
- No hardcoded credentials
- Input validation on all API endpoints

---

## [Unreleased]

### Planned
- PostgreSQL support for production
- User authentication system
- Role-based access control
- Webhook notifications
- More asset data sources
