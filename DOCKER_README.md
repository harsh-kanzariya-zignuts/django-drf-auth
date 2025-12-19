# 🐳 Docker Setup Guide - Django Auth System

Complete guide for running the Django authentication system with Docker.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [File Structure](#file-structure)
- [Configuration Files](#configuration-files)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## 🎯 Prerequisites

Before you begin, ensure you have:

- **Docker** (20.10+): [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (2.0+): [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Git**: For cloning the repository

Verify installations:

```bash
docker --version
docker-compose --version
```

---

## ⚡ Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd <project-directory>

# Copy environment file
cp .env.example .env

# IMPORTANT: Edit .env and change these values:
# - DJANGO_SECRET_KEY (generate a secure one)
# - POSTGRES_PASSWORD (use a strong password)
# - EMAIL settings (if using email features)
```

### 2. Build and Run

```bash
# Build images
docker-compose build

# Start services (with hot reload for development)
docker-compose up

# Or run in background
docker-compose up -d
```

### 3. Access the Application

- **API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs** (after Swagger setup): http://localhost:8000/api/docs/

### 4. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser --email admin@example.com
```

### 5. Stop Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (⚠️ deletes database)
docker-compose down -v
```

---

## 📁 File Structure

```
project/
├── Dockerfile                      # Production-grade multi-stage build
├── docker-compose.yml              # Base configuration (production-like)
├── docker-compose.override.yml     # Development overrides (auto-applied)
├── docker-compose.test.yml         # Testing configuration
├── .dockerignore                   # Files to exclude from Docker build
├── .env                           # Environment variables (create from .env.example)
├── .env.example                    # Environment template
└── requirements/
    ├── base.txt                   # Core dependencies
    └── development.txt            # Dev dependencies
```

---

## ⚙️ Configuration Files

### 1. **Dockerfile** (Multi-Stage Build)

**Purpose**: Creates optimized, production-ready Docker image

**Key Features**:

- ✅ Multi-stage build (smaller images)
- ✅ Non-root user (security)
- ✅ Health checks (K8s/ECS ready)
- ✅ Optimized layer caching

**Size Optimization**:

- Builder stage: ~800MB (temporary)
- Final image: ~250MB (deployed)

### 2. **docker-compose.yml** (Base Configuration)

**Purpose**: Production-like setup using Gunicorn

**Services**:

- `db`: PostgreSQL 16 (Alpine Linux)
- `web`: Django app with Gunicorn

**Usage**:

```bash
# Use with production settings
docker-compose -f docker-compose.yml up
```

### 3. **docker-compose.override.yml** (Development Mode)

**Purpose**: Adds development convenience features

**Features**:

- ✅ Live code reload (volume mounting)
- ✅ Django runserver (auto-reload)
- ✅ Debug mode enabled
- ✅ Interactive shell support

**Auto-applied** when you run `docker-compose up`

**To ignore** (test production behavior):

```bash
docker-compose -f docker-compose.yml up
```

### 4. **docker-compose.test.yml** (Testing)

**Purpose**: Isolated test environment

**Features**:

- ✅ In-memory database (fast)
- ✅ Separate network
- ✅ Coverage reports
- ✅ CI/CD compatible

---

## 💻 Development Workflow

### Starting Development

```bash
# Start with hot reload (override applied automatically)
docker-compose up

# Or in background
docker-compose up -d

# View logs
docker-compose logs -f web
```

### Running Management Commands

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser --email admin@example.com

# Django shell
docker-compose exec web python manage.py shell

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Database Management

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U authuser -d authdb

# Backup database
docker-compose exec db pg_dump -U authuser authdb > backup.sql

# Restore database
docker-compose exec -T db psql -U authuser authdb < backup.sql

# Reset database (⚠️ deletes all data)
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### Code Changes

With `docker-compose.override.yml`:

- ✅ Code changes auto-reload
- ✅ No rebuild needed
- ✅ Immediate feedback

### Rebuilding

When to rebuild:

- ❗ Changed `requirements/*.txt`
- ❗ Modified `Dockerfile`
- ❗ Added system dependencies

```bash
# Rebuild specific service
docker-compose build web

# Rebuild all services
docker-compose build

# Force rebuild (no cache)
docker-compose build --no-cache
```

---

## 🧪 Testing

### Run All Tests

```bash
# Using dedicated test compose file
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Or run tests in main web container
docker-compose exec web pytest -v
```

### Run Specific Tests

```bash
# Test specific app
docker-compose exec web pytest apps/authentication/tests/ -v

# Test specific file
docker-compose exec web pytest apps/authentication/tests/test_authentication.py -v

# Test specific function
docker-compose exec web pytest apps/authentication/tests/test_authentication.py::TestAuthentication::test_user_login -v

# Run with keyword filter
docker-compose exec web pytest -k "login" -v
```

### Coverage Reports

```bash
# Generate coverage report
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Coverage files will be in:
# - htmlcov/index.html (open in browser)
# - coverage.xml (for CI/CD)
# - .coverage (raw data)

# Or run coverage manually
docker-compose exec web pytest --cov=apps --cov-report=html --cov-report=term-missing
```

### CI/CD Testing

```bash
# Exact command for CI pipelines
docker-compose -f docker-compose.test.yml build
docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test
```

---

## 🚀 Production Deployment

### 1. Environment Setup

```bash
# Create production .env
cp .env.example .env.production

# Edit .env.production:
DJANGO_ENV=production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<generate-strong-secret-key>
POSTGRES_PASSWORD=<strong-production-password>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. Production Compose File

Create `docker-compose.production.yml`:

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  web:
    build:
      context: .
      dockerfile: Dockerfile
    command: >
      sh -c "
      python manage.py migrate --noinput &&
      python manage.py collectstatic --noinput &&
      gunicorn config.wsgi:application
      --bind 0.0.0.0:8000
      --workers 4
      --threads 2
      --worker-class gthread
      --timeout 120
      --access-logfile -
      --error-logfile -
      --log-level info
      "
    env_file:
      - .env.production
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.production
    ports:
      - "8000:8000"
    depends_on:
      - db
    restart: always

volumes:
  postgres_data:
```

### 3. Deploy

```bash
# Build production image
docker-compose -f docker-compose.production.yml build

# Start production services
docker-compose -f docker-compose.production.yml up -d

# Check logs
docker-compose -f docker-compose.production.yml logs -f

# Create superuser
docker-compose -f docker-compose.production.yml exec web python manage.py createsuperuser
```

### 4. Production Best Practices

- ✅ Use environment variables for secrets
- ✅ Enable SSL/TLS (use nginx/traefik as reverse proxy)
- ✅ Set up monitoring (Sentry, Prometheus)
- ✅ Configure log aggregation
- ✅ Regular database backups
- ✅ Use Docker secrets for sensitive data
- ✅ Implement rate limiting
- ✅ Set up health checks

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Error: port 8000 is already allocated

# Solution: Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 on host

# Or stop conflicting service
lsof -ti:8000 | xargs kill -9
```

#### 2. Database Connection Error

```bash
# Error: could not connect to server

# Solution 1: Wait for database to be ready
docker-compose up -d db
# Wait 10 seconds
docker-compose up web

# Solution 2: Check database health
docker-compose ps
docker-compose logs db

# Solution 3: Reset database
docker-compose down -v
docker-compose up -d
```

#### 3. Permission Denied

```bash
# Error: Permission denied (staticfiles/media)

# Solution: Fix ownership
docker-compose exec web chown -R django:django /app/staticfiles /app/media

# Or rebuild with proper user
docker-compose build --no-cache
```

#### 4. Module Not Found

```bash
# Error: ModuleNotFoundError

# Solution: Rebuild after dependency changes
docker-compose build web
docker-compose up -d web
```

#### 5. Container Exits Immediately

```bash
# Check logs
docker-compose logs web

# Common causes:
# - Syntax error in code
# - Missing migration
# - Environment variable issue

# Debug interactively
docker-compose run --rm web bash
python manage.py check
```

### Useful Debug Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs web
docker-compose logs db
docker-compose logs -f --tail=100 web

# Access container shell
docker-compose exec web bash

# Check environment variables
docker-compose exec web env

# Inspect container
docker inspect auth_web

# Check networks
docker network ls
docker network inspect <network-name>

# Remove everything and start fresh
docker-compose down -v --rmi all
docker-compose build --no-cache
docker-compose up
```

---

## 🎓 Advanced Usage

### Custom Commands

Create `docker-compose.override.local.yml` for personal overrides:

```yaml
version: "3.9"

services:
  web:
    environment:
      - DEBUG_TOOLBAR=True
    ports:
      - "8001:8000"
```

Use it:

```bash
docker-compose -f docker-compose.yml -f docker-compose.override.local.yml up
```

### Multi-Environment Setup

```bash
# Development
docker-compose up

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up

# Production
docker-compose -f docker-compose.production.yml up
```

### Scaling Services

```bash
# Scale web workers (requires load balancer)
docker-compose up -d --scale web=3
```

### Using with Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.production.yml auth_stack

# Check status
docker stack services auth_stack

# Remove stack
docker stack rm auth_stack
```

### Health Check Commands

```bash
# Manual health check
docker-compose exec web curl http://localhost:8000/admin/

# Check all container health
docker-compose ps

# Watch health status
watch docker-compose ps
```

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "0.5"
          memory: 512M
```

---

## 📊 Monitoring

### View Container Stats

```bash
# Real-time stats
docker stats

# Specific container
docker stats auth_web

# Export metrics
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Logs Management

```bash
# Follow logs
docker-compose logs -f

# Last N lines
docker-compose logs --tail=50 web

# Since timestamp
docker-compose logs --since 2024-01-01T00:00:00 web

# Save logs to file
docker-compose logs > app.log
```

---

## 🔐 Security Checklist

- [ ] Changed `DJANGO_SECRET_KEY` in production
- [ ] Used strong `POSTGRES_PASSWORD`
- [ ] Enabled SSL/TLS in production
- [ ] Set `DJANGO_DEBUG=False` in production
- [ ] Restricted `ALLOWED_HOSTS`
- [ ] Enabled security headers (HSTS, CSP)
- [ ] Running as non-root user
- [ ] Regular security updates
- [ ] Database backups configured
- [ ] Secrets not in version control

---

## 🎯 Quick Reference

### Essential Commands

```bash
# Development
docker-compose up -d                    # Start dev environment
docker-compose logs -f web              # View logs
docker-compose exec web bash            # Access shell
docker-compose down                     # Stop services

# Testing
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Production
docker-compose -f docker-compose.production.yml up -d

# Rebuild
docker-compose build                    # Rebuild images
docker-compose up -d --force-recreate   # Recreate containers

# Clean up
docker-compose down -v                  # Remove volumes
docker system prune -a                  # Clean everything
```

### Keyboard Shortcuts (in logs)

- `Ctrl+C`: Stop viewing logs (containers keep running)
- `Ctrl+C` (twice): Stop containers

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

## 🆘 Need Help?

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. View container logs: `docker-compose logs -f web`
3. Check GitHub Issues
4. Contact the development team

---

**Last Updated**: December 2025  
**Docker Version**: 24.0+  
**Docker Compose Version**: 2.0+
