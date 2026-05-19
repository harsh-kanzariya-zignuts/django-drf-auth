# 🔐 Django Authentication System with JWT & Social OAuth

A production-ready Django REST API with complete authentication features, UUID primary keys, full audit trail, and Docker deployment.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### 🔐 Authentication

- ✅ Email/Password registration & login
- ✅ JWT authentication with auto-refresh
- ✅ Social OAuth (Google, Facebook, GitHub)
- ✅ Email verification
- ✅ Password reset flow
- ✅ Token blacklisting on logout

### 👤 User Management

- ✅ UUID primary keys (enhanced security)
- ✅ Full audit trail (created_by, updated_by, deleted_by)
- ✅ Soft delete functionality
- ✅ Custom user managers
- ✅ Profile management

### 🏗️ Architecture

- ✅ Clean code structure
- ✅ Base models for inheritance
- ✅ Custom exception handling
- ✅ Environment-based configuration (`DJANGO_ENV` switcher)
- ✅ Production-ready settings

### 🐳 Docker

- ✅ Multi-stage Dockerfile (optimized)
- ✅ Docker Compose for orchestration
- ✅ Separate dev/test/prod configurations
- ✅ Health checks on all services (`/health/` endpoint)
- ✅ Redis password auth
- ✅ Log rotation + resource limits
- ✅ CI/CD ready

### 🧪 Testing

- ✅ Comprehensive test suite
- ✅ Pytest configuration
- ✅ Coverage reports
- ✅ Isolated test environment (tmpfs, no `.env` dependency)

---

## 🛠️ Tech Stack

| Category | Technology |
| --- | --- |
| **Backend** | Django 5.x, Django REST Framework |
| **Authentication** | django-allauth, dj-rest-auth, simplejwt |
| **Database** | PostgreSQL 16 |
| **Cache / Broker** | Redis 7 |
| **Task Queue** | Celery + Celery Beat |
| **Web Server** | Gunicorn |
| **Containerization** | Docker, Docker Compose |
| **Testing** | Pytest, pytest-django, pytest-cov |
| **Code Quality** | Ruff (linter & formatter) |

---

## 🚀 Quick Start

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env — at minimum set these three:
#    DJANGO_SECRET_KEY=<generate a secure one>
#    POSTGRES_PASSWORD=<strong password>
#    REDIS_PASSWORD=<strong password>
#    CELERY_BROKER_URL=redis://:yourpassword@redis:6379/0
#    CELERY_RESULT_BACKEND=redis://:yourpassword@redis:6379/1

# 3. Build and start services
docker compose up --build

# 4. Create superuser
docker compose exec web python manage.py createsuperuser --email admin@example.com
```

### Access the Application

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Admin Panel | http://localhost:8000/admin/ |
| Health Check | http://localhost:8000/health/ |
| API Docs | http://localhost:8000/api/docs/ |

> For full Docker setup details, environment variables, testing, and production
> deployment — see **[DOCKER_README.md](DOCKER_README.md)**.

---

## 🔌 API Endpoints

### Authentication

| Endpoint | Method | Auth | Description |
| --- | --- | --- | --- |
| `/api/auth/register/` | POST | No | Register new user |
| `/api/auth/login/` | POST | No | Login with credentials |
| `/api/auth/logout/` | POST | Yes | Logout (blacklist token) |
| `/api/auth/token/refresh/` | POST | No | Refresh access token |
| `/api/auth/verify-email/` | POST | No | Verify email address |
| `/api/auth/password/reset/` | POST | No | Request password reset |
| `/api/auth/password/change/` | POST | Yes | Change password |

### User Profile

| Endpoint | Method | Auth | Description |
| --- | --- | --- | --- |
| `/api/auth/profile/` | GET | Yes | Get current user profile |
| `/api/auth/profile/update/` | PATCH | Yes | Update user profile |

### Social Authentication

| Endpoint | Method | Auth | Description |
| --- | --- | --- | --- |
| `/api/auth/social/google/` | POST | No | Google OAuth login |
| `/api/auth/social/facebook/` | POST | No | Facebook OAuth login |
| `/api/auth/social/github/` | POST | No | GitHub OAuth login |
| `/api/auth/social/accounts/` | GET | Yes | List connected accounts |
| `/api/auth/social/disconnect/<provider>/` | DELETE | Yes | Disconnect social account |

### System

| Endpoint | Method | Auth | Description |
| --- | --- | --- | --- |
| `/health/` | GET | No | Health check (DB + cache status) |
| `/api/docs/` | GET | No | Swagger UI |
| `/api/schema/` | GET | No | OpenAPI schema |

---

## 📁 Project Structure

```
project/
├── apps/
│   ├── authentication/          # Auth logic (serializers, views, adapters, tasks)
│   ├── health/                  # /health/ endpoint
│   └── users/                   # User model and management
├── common/                      # Base models, managers, utilities, exceptions
├── config/
│   ├── settings/
│   │   ├── __init__.py         # DJANGO_ENV-based settings switcher
│   │   ├── base.py             # Common settings
│   │   ├── development.py      # Dev-specific overrides
│   │   ├── testing.py          # Test-specific overrides
│   │   └── production.py       # Production settings
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # WSGI application
├── requirements/
│   ├── base.txt                # Core dependencies
│   └── development.txt         # Dev + test dependencies
├── Dockerfile                   # Multi-stage build (builder + runtime)
├── docker-compose.yml           # Base config (all environments)
├── docker-compose.override.yml  # Dev overrides (auto-applied, hot reload)
├── docker-compose.test.yml      # Standalone test runner
├── .dockerignore                # Docker build exclusions
├── .env.example                 # Environment template
├── DOCKER_README.md             # Full Docker + deployment guide
├── manage.py                    # Django management
└── pyproject.toml               # Python project config (pytest, ruff)
```

---

## 💻 Development Workflow

### Using Docker (recommended)

```bash
# Start all services with hot reload
docker compose up -d

# View logs
docker compose logs -f web

# Run management commands
docker compose exec web python manage.py <command>

# Stop services
docker compose down
```

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/development.txt

# Edit .env — set POSTGRES_HOST=localhost and local DB credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 🧪 Testing

```bash
# Run full test suite with coverage
docker compose -f docker-compose.test.yml up --abort-on-container-exit

# Run specific tests in the dev container
docker compose exec web pytest apps/authentication/tests/ -v
docker compose exec web pytest -k "login" -v
```

See [DOCKER_README.md](DOCKER_README.md#testing) for CI pipeline commands and coverage report details.

---

## 🚀 Production Deployment

See [DOCKER_README.md](DOCKER_README.md#production-deployment) for the full production guide including environment setup, deployment commands, and the production checklist.

**Quick summary:**
```bash
# Use base file only — no override in production
docker compose -f docker-compose.yml --env-file .env.production up -d --build
```

---

## 🔧 Environment Variables

See [DOCKER_README.md](DOCKER_README.md#environment-variables) for the complete reference.

**Minimum required to start:**

```bash
DJANGO_SECRET_KEY=        # no default — must be set
POSTGRES_PASSWORD=        # no default — must be set
REDIS_PASSWORD=           # no default — must be set
CELERY_BROKER_URL=redis://:yourpassword@redis:6379/0
CELERY_RESULT_BACKEND=redis://:yourpassword@redis:6379/1
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Run the test suite: `docker compose -f docker-compose.test.yml up --abort-on-container-exit`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push and open a Pull Request

---

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: Production Ready
- **Last Updated**: May 2026

---

**Made with ❤️ using Django and Docker**