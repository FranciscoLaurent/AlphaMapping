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
