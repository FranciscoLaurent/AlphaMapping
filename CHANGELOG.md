# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
