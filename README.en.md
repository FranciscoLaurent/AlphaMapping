# AlphaMapping

**Industrial-Grade Cyberspace Asset Situational Awareness Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](docker-compose.yml)

[中文](README.md) | English

![Dashboard Preview](image.png)

AlphaMapping is a next-generation cyberspace asset query and intelligent analysis system. It deeply integrates multi-platform asset mapping (FOFA, ZoomEye) with AI large language models (LLM), providing natural language interaction, real-time situational awareness dashboards, and automated security risk assessment.

> 💡 **Design Philosophy: Standing on the Shoulders of Giants**
>
> AlphaMapping **does NOT perform any active scanning**. Instead, it fully leverages the data capabilities of mature cyberspace mapping platforms like FOFA and ZoomEye. We focus on:
> - 🔗 **Data Aggregation**: Unified multi-platform API interface, eliminating redundant queries
> - 🧠 **Intelligent Analysis**: AI-powered deep analysis of asset exposure risks
> - 📊 **Visualization**: Transform complex data into intuitive situational awareness dashboards

## ✨ Key Features

### 🖥️ Situational Awareness Dashboard
- **Cyberpunk Design**: Glassmorphism dark-themed dashboard designed for SOC monitoring centers
- **Real-time Visualization**: ECharts dynamic charts — port distribution, protocol analysis, global geo heatmap
- **Interactive Linking**: Click charts to filter asset list, map scatter points highlight asset cards
- **5-Column Grid Layout**: Compact asset cards displaying more information per screen

### 🤖 AI Intelligence Engine
- **NL2CSEQL Translation**: Natural language → Platform query syntax (e.g., "Find Apache servers in Beijing")
- **Security Risk Reports**: AI auto-analyzes asset exposure, generates risk levels, vulnerability correlations, remediation recommendations
- **Single Asset Deep Analysis**: One-click AI security assessment for individual assets

### 📡 Multi-Source Data Fusion
- **Dual Platform Support**: FOFA + ZoomEye out-of-the-box, extensible for more data sources
- **Smart Caching**: Same queries hit local cache first, saving API quota
- **Data Deduplication**: IP:Port unique constraint with automatic Upsert updates

### 📊 Data Management
- **Advanced Filtering**: Multi-dimensional filtering by keyword, country, protocol, port
- **Multi-Format Export**: CSV / Excel / JSON one-click download
- **Scheduled Tasks**: Cron expression configuration for automated asset updates

### 🐳 Ready to Deploy
- **Docker One-Click Deployment**: `docker-compose up -d` to start
- **PowerShell Scripts**: Windows environment automation
- **OpenAPI Documentation**: FastAPI auto-generated interactive API docs

---

## 🏗️ Architecture

| Layer | Tech Stack |
| --- | --- |
| **Backend** | FastAPI, SQLAlchemy, Pydantic, OpenAI SDK, APScheduler |
| **Frontend** | Vanilla JS (ES6+), CSS3, ECharts 5 |
| **Database** | SQLite (dev) / PostgreSQL (production-ready) |
| **Deployment** | Docker, docker-compose, Nginx, PowerShell |
| **Testing** | pytest, pytest-cov, pytest-asyncio |

```
AlphaMapping/
├── backend/           # FastAPI Backend
│   ├── app/
│   │   ├── core/      # Configuration, Database
│   │   ├── models/    # ORM Models
│   │   ├── services/  # Business Logic
│   │   └── main.py    # API Routes
│   └── tests/         # Unit Tests
├── frontend/          # Static Frontend
├── docker/            # Container Configuration
└── scripts/           # Automation Scripts
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- (Optional) Docker & Docker Compose

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/your-repo/AlphaMapping.git
cd AlphaMapping

# 2. Configure API keys
cp backend/.env.example backend/.env
# Edit backend/.env with FOFA_KEY, ZOOMEYE_KEY, OPENAI_API_KEY

# 3. Start services
# Windows (PowerShell)
./scripts/run.ps1

# Linux / macOS
chmod +x scripts/*.sh
./scripts/run.sh

# Access
# - Frontend: http://localhost:3000
# - API Docs: http://localhost:8000/docs

# Stop services
# Windows: ./scripts/stop.ps1
# Linux/macOS: ./scripts/stop.sh
```

### Docker Deployment

```bash
# Configure environment
cp backend/.env.example .env
# Edit .env with your keys

# Start containers
docker-compose up -d

# Access
# - Frontend: http://localhost
# - API: http://localhost:8000
```

## ⚙️ Configuration

Create `.env` file with:

```env
# FOFA API
FOFA_EMAIL=your_email
FOFA_KEY=your_api_key

# ZoomEye API
ZOOMEYE_KEY=your_api_key

# LLM Configuration (OpenAI-compatible)
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

## 🧪 Testing

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v --cov=app
```

## 📖 API Overview

| Endpoint | Method | Description |
| --- | --- | --- |
| `/query` | POST | Execute asset query |
| `/assets` | GET | List assets with filters |
| `/assets/export` | GET | Export assets (csv/excel/json) |
| `/analyze/{query_id}` | POST | Generate AI analysis report |
| `/scheduled-tasks` | CRUD | Manage scheduled tasks |
| `/stats` | GET | Dashboard statistics |

Full API documentation available at `/docs` when running.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

## 🔒 Security

For security issues, please see our [Security Policy](SECURITY.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

*AlphaMapping - Mapping the Unknown in Cyberspace.*
