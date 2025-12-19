# 🔐 Django Authentication System with JWT & Social OAuth

A production-ready Django REST API with complete authentication features, UUID primary keys, full audit trail, and Docker deployment.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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
- ✅ Environment-based configuration
- ✅ Production-ready settings

### 🐳 Docker

- ✅ Multi-stage Dockerfile (optimized)
- ✅ Docker Compose for orchestration
- ✅ Separate dev/test/prod configurations
- ✅ Health checks & monitoring
- ✅ CI/CD ready

### 🧪 Testing

- ✅ Comprehensive test suite
- ✅ Pytest configuration
- ✅ Coverage reports
- ✅ Isolated test environment

---

## 🛠️ Tech Stack

| Category             | Technology                              |
| -------------------- | --------------------------------------- |
| **Backend**          | Django 5.0, Django REST Framework       |
| **Authentication**   | django-allauth, dj-rest-auth, simplejwt |
| **Database**         | PostgreSQL 16                           |
| **Web Server**       | Gunicorn                                |
| **Containerization** | Docker, Docker Compose                  |
| **Testing**          | Pytest, pytest-django, pytest-cov       |
| **Code Quality**     | Ruff (linter & formatter)               |

---

## 🚀 Quick Start

### Manual Setup

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env and change:
#    - DJANGO_SECRET_KEY
#    - POSTGRES_PASSWORD
#    - EMAIL settings

# 3. Build and start services
docker-compose build
docker-compose up -d

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Access the Application

- **API Base URL**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/

---

## 🔌 API Endpoints

### Authentication

| Endpoint                     | Method | Auth | Description              |
| ---------------------------- | ------ | ---- | ------------------------ |
| `/api/auth/register/`        | POST   | No   | Register new user        |
| `/api/auth/login/`           | POST   | No   | Login with credentials   |
| `/api/auth/logout/`          | POST   | Yes  | Logout (blacklist token) |
| `/api/auth/token/refresh/`   | POST   | No   | Refresh access token     |
| `/api/auth/verify-email/`    | POST   | No   | Verify email address     |
| `/api/auth/password/reset/`  | POST   | No   | Request password reset   |
| `/api/auth/password/change/` | POST   | Yes  | Change password          |

### User Profile

| Endpoint                    | Method | Auth | Description              |
| --------------------------- | ------ | ---- | ------------------------ |
| `/api/auth/profile/`        | GET    | Yes  | Get current user profile |
| `/api/auth/profile/update/` | PATCH  | Yes  | Update user profile      |

### Social Authentication

| Endpoint                                  | Method | Auth | Description               |
| ----------------------------------------- | ------ | ---- | ------------------------- |
| `/api/auth/social/google/`                | POST   | No   | Google OAuth login        |
| `/api/auth/social/facebook/`              | POST   | No   | Facebook OAuth login      |
| `/api/auth/social/github/`                | POST   | No   | GitHub OAuth login        |
| `/api/auth/social/accounts/`              | GET    | Yes  | List connected accounts   |
| `/api/auth/social/disconnect/<provider>/` | DELETE | Yes  | Disconnect social account |

---

## 📁 Project Structure

```
project/
├── apps/
│   ├── authentication/          # Auth logic (serializers, views, adapters)
│   └── users/                   # User model and management
├── common/                      # Base models, managers, utilities
├── config/
│   ├── settings/
│   │   ├── base.py             # Common settings
│   │   ├── development.py      # Dev-specific settings
│   │   ├── testing.py          # Test-specific settings
│   │   └── production.py       # Production settings
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py                 # WSGI application
├── requirements/
│   ├── base.txt                # Core dependencies
│   └── development.txt         # Dev dependencies
├── Dockerfile                   # Multi-stage production Dockerfile
├── docker-compose.yml           # Base Docker Compose config
├── docker-compose.override.yml  # Dev overrides (hot reload)
├── docker-compose.test.yml      # Testing configuration
├── .dockerignore               # Docker build exclusions
├── .env.example                 # Environment template
├── manage.py                   # Django management
└── pyproject.toml              # Python project config
```

---

## 💻 Development Workflow

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f web

# Run commands
docker-compose exec web python manage.py <command>

# Stop services
docker-compose down
```

### Local Development (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements/development.txt

# Setup database (PostgreSQL required)
# Edit .env with local database credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## 🧪 Testing

### Run All Tests

```bash

# Using Docker Compose
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Using existing container
docker-compose exec web pytest -v
```

### Run Specific Tests

```bash
# Specific file
docker-compose exec web pytest apps/authentication/tests/test_authentication.py -v

# Specific test
docker-compose exec web pytest apps/authentication/tests/test_authentication.py::TestAuthentication::test_user_login -v

# By keyword
docker-compose exec web pytest -k "login" -v
```

---

## 🚀 Production Deployment

### Prerequisites

1. **Server** with Docker installed
2. **Domain name** pointed to your server
3. **SSL certificate** (use Let's Encrypt)
4. **Environment variables** configured

### Deployment Steps

1. **Clone repository on server**

```bash
git clone <your-repo-url>
cd <project-directory>
```

2. **Create production environment**

```bash
cp .env.example .env.production

# Edit .env.production:
# - Set DJANGO_ENV=production
# - Set DJANGO_DEBUG=False
# - Generate new DJANGO_SECRET_KEY
# - Use strong POSTGRES_PASSWORD
# - Configure ALLOWED_HOSTS
# - Enable security settings
```

3. **Build and start**

```bash
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

4. **Run migrations and collect static**

```bash
docker-compose -f docker-compose.production.yml exec web python manage.py migrate
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
```

5. **Create superuser**

```bash
docker-compose -f docker-compose.production.yml exec web python manage.py createsuperuser
```

### Production Checklist

- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY` generated
- [ ] Strong database password
- [ ] `ALLOWED_HOSTS` configured
- [ ] SSL/TLS enabled
- [ ] Security headers enabled
- [ ] Database backups configured
- [ ] Error tracking (Sentry) setup
- [ ] Log aggregation configured
- [ ] Monitoring setup
- [ ] Regular security updates

---

## 🔧 Environment Variables

### Required Variables

```bash
DJANGO_SECRET_KEY=<generate-secure-key>
POSTGRES_DB=authdb
POSTGRES_USER=authuser
POSTGRES_PASSWORD=<strong-password>
POSTGRES_HOST=db  # or localhost for local dev
```

### Optional Variables

```bash
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
FRONTEND_URL=http://localhost:3000
SENTRY_DSN=<your-sentry-dsn>
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Use meaningful commit messages
- Run tests before submitting PR

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **Documentation**: Check the docs in the repository
- **Issues**: [GitHub Issues](https://github.com/yourusername/yourproject/issues)
- **Email**: your-email@example.com

---

## 🙏 Acknowledgments

- Django and Django REST Framework teams
- django-allauth and dj-rest-auth maintainers
- All contributors and supporters

---

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: Production Ready
- **Last Updated**: December 2025

---

**Made with ❤️ using Django and Docker**
