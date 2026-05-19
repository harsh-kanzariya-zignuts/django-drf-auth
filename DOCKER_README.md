# 🐳 Docker Setup Guide - Django Auth System

Complete guide for running the Django authentication system with Docker.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [File Structure](#file-structure)
- [Configuration Files](#configuration-files)
- [Environment Variables](#environment-variables)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## 🎯 Prerequisites

Before you begin, ensure you have:

- **Docker** (24.0+): [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (2.0+): Included with Docker Desktop
- **Git**: For cloning the repository

Verify installations:

```bash
docker --version
docker compose version
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

# Edit .env — at minimum set these before starting:
# DJANGO_SECRET_KEY=<generate a secure one>
# POSTGRES_PASSWORD=<strong password>
# REDIS_PASSWORD=<strong password>
# CELERY_BROKER_URL=redis://:yourpassword@redis:6379/0   ← must match REDIS_PASSWORD
# CELERY_RESULT_BACKEND=redis://:yourpassword@redis:6379/1
```

### 2. Build and Run

```bash
# Build images and start all services (development mode with hot reload)
docker compose up --build

# Or run in background
docker compose up -d --build
```

### 3. Access the Application

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Admin Panel | http://localhost:8000/admin/ |
| Health Check | http://localhost:8000/health/ |
| API Docs (Swagger) | http://localhost:8000/api/docs/ |
| PostgreSQL (host) | localhost:5440 |
| Redis (host) | localhost:6379 |

> PostgreSQL and Redis are exposed to your host machine in development so you can
> connect with tools like pgAdmin, TablePlus, or the VS Code Redis extension.
> Both are bound to `127.0.0.1` only — not accessible from your network.

### 4. Create Superuser

```bash
docker compose exec web python manage.py createsuperuser --email admin@example.com
```

### 5. Stop Services

```bash
# Stop containers (keeps volumes/data)
docker compose down

# Stop and remove volumes (⚠️ deletes database and Redis data)
docker compose down -v
```

---

## 📁 File Structure

```
project/
├── Dockerfile                      # Multi-stage build (builder + runtime)
├── docker-compose.yml              # Base configuration (production-like)
├── docker-compose.override.yml     # Development overrides (auto-applied)
├── docker-compose.test.yml         # Standalone test runner
├── .dockerignore                   # Files excluded from Docker build context
├── .env                            # Your local environment variables (never commit)
├── .env.example                    # Template — copy this to .env
└── requirements/
    ├── base.txt                    # Core dependencies
    └── development.txt             # Dev + test dependencies
```

---

## ⚙️ Configuration Files

### 1. `Dockerfile` (Multi-Stage Build)

Two stages to keep the final image lean:

- **Builder stage**: installs build tools and Python packages (~800MB, temporary)
- **Runtime stage**: copies only what's needed to run (~250MB, deployed)

Key features:
- ✅ Non-root user (`django`) for security
- ✅ `curl` installed for healthchecks
- ✅ `libpq5` for PostgreSQL client
- ✅ `PYTHONDONTWRITEBYTECODE` and `PYTHONUNBUFFERED` set correctly

### 2. `docker-compose.yml` (Base Configuration)

Production-like setup. Defines all services with security and reliability in mind.

**Services:**

| Service | Image | Purpose |
|---|---|---|
| `db` | postgres:16-alpine | PostgreSQL database |
| `redis` | redis:7-alpine | Cache + Celery broker |
| `web` | local build | Django + Gunicorn |
| `celery` | local build | Background task worker |
| `celery-beat` | local build | Periodic task scheduler |

**Key features:**
- ✅ Redis password auth (`--requirepass`)
- ✅ Redis not exposed to host (internal network only in base file)
- ✅ All services have `restart: unless-stopped`
- ✅ Health checks on all services with proper `start_period`
- ✅ YAML anchors eliminate repeated config blocks
- ✅ Log rotation (10MB max, 3 files) on all services
- ✅ Resource limits (memory + CPU) on app services
- ✅ Celery Beat pidfile prevents duplicate schedulers

### 3. `docker-compose.override.yml` (Development Mode)

Auto-merged by Docker Compose when you run `docker compose up`. Only contains
what's different from production — not a full duplicate of the base file.

**What it changes:**
- Runs Django dev server instead of Gunicorn (hot reload)
- Bind-mounts source code (`.:/app`) for live editing without rebuilding
- Sets `DJANGO_DEBUG=True`
- Exposes PostgreSQL on `127.0.0.1:5440` for pgAdmin / TablePlus / DataGrip
- Exposes Redis on `127.0.0.1:6379` for the VS Code Redis extension

**To run without override** (test production Gunicorn behaviour):
```bash
docker compose -f docker-compose.yml up
```

### 4. `docker-compose.test.yml` (Test Runner)

Fully standalone — do **not** merge with the base file (see [Testing](#testing) for why).

**What makes it different:**
- In-memory tmpfs for PostgreSQL and Redis (fast, no disk I/O)
- Hardcoded test credentials (isolated, no real secrets needed)
- No Redis password (not needed in isolated test network)
- All required env vars declared explicitly (no `.env` file dependency)
- `restart: "no"` so failures exit cleanly for CI

---

## 🔧 Environment Variables

### How settings work

This project uses a custom settings switcher in `config/settings/__init__.py`:

```python
env = os.getenv("DJANGO_ENV", "development")
module = import_module(f".{env}", "config.settings")
```

`DJANGO_SETTINGS_MODULE` is **always** `config.settings` — it never changes between environments.
`DJANGO_ENV` is what controls which settings file actually loads:

| `DJANGO_ENV` | Settings file loaded |
|---|---|
| `development` (default if unset) | `config/settings/development.py` |
| `production` | `config/settings/production.py` |
| `testing` | `config/settings/testing.py` |

### Complete `.env` reference

```bash
# ── Environment ──────────────────────────────────────────────────────────────
DJANGO_ENV=development             # Controls which settings file loads
DJANGO_SECRET_KEY=                 # Required. Generate with:
                                   # python -c "import secrets; print(secrets.token_urlsafe(50))"
DJANGO_DEBUG=True                  # Set False in production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_LOG_LEVEL=INFO

# ── Database ─────────────────────────────────────────────────────────────────
POSTGRES_DB=authdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=                 # Required. Use a strong password.
POSTGRES_HOST=db                   # Always "db" when running in Docker
POSTGRES_PORT=5432

# Local development without Docker (comment out the Docker block above):
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5433              # Use a different port if 5432 is taken locally

# ── Redis ────────────────────────────────────────────────────────────────────
REDIS_PASSWORD=                    # Required. Used by Redis --requirepass and broker URLs.

# ⚠️  IMPORTANT: broker URLs must include the password to match Redis auth.
#     In Docker:     redis://:yourpassword@redis:6379/0
#     Without Docker (local): redis://localhost:6379/0  (if no local Redis password)
CELERY_BROKER_URL=redis://:yourpassword@redis:6379/0
CELERY_RESULT_BACKEND=redis://:yourpassword@redis:6379/1

# ── Gunicorn / Celery tuning (optional) ──────────────────────────────────────
GUNICORN_WORKERS=3
GUNICORN_TIMEOUT=120
CELERY_CONCURRENCY=4

# ── Frontend ─────────────────────────────────────────────────────────────────
FRONTEND_URL=http://localhost:3000
SOCIALACCOUNT_CALLBACK_URL=http://localhost:3000/auth/callback

# ── Email ────────────────────────────────────────────────────────────────────
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@example.com

# ── Authentication ───────────────────────────────────────────────────────────
ACCOUNT_EMAIL_VERIFICATION=optional   # Use "mandatory" in production

# ── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ── Security (set True in production) ────────────────────────────────────────
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0

# ── Social OAuth (leave blank if not using) ───────────────────────────────────
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# ── Monitoring (optional) ────────────────────────────────────────────────────
SENTRY_DSN=
```

### ⚠️ Common `.env` mistake — Redis password mismatch

Your Redis container starts with `--requirepass ${REDIS_PASSWORD}`, so your
broker URLs **must** include the password:

```bash
# ❌ Wrong — connection will be refused (NOAUTH error)
REDIS_PASSWORD=abc123
CELERY_BROKER_URL=redis://redis:6379/0

# ✅ Correct — password included in URL
REDIS_PASSWORD=abc123
CELERY_BROKER_URL=redis://:abc123@redis:6379/0
CELERY_RESULT_BACKEND=redis://:abc123@redis:6379/1
```

---

## 💻 Development Workflow

### Starting Development

```bash
# Start with hot reload (override applied automatically)
docker compose up

# Background mode
docker compose up -d

# View logs
docker compose logs -f web
docker compose logs -f celery
```

### Running Management Commands

```bash
# Migrations
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser --email admin@example.com

# Django shell
docker compose exec web python manage.py shell

# Check for configuration issues
docker compose exec web python manage.py check
```

### Database Management

```bash
# Access PostgreSQL shell (via Docker)
docker compose exec db psql -U postgres -d authdb

# Or connect with any DB tool using:
# Host: localhost  Port: 5440  DB: authdb  User: postgres

# Backup
docker compose exec db pg_dump -U postgres authdb > backup.sql

# Restore
docker compose exec -T db psql -U postgres authdb < backup.sql

# Reset database (⚠️ deletes all data)
docker compose down -v
docker compose up -d
```

### Connecting to Redis

In development, Redis is exposed on `localhost:6379`:

```bash
# VS Code Redis extension: redis://localhost:6379 (no password prompt needed from host)
# Redis CLI:
redis-cli -p 6379
# or with password:
redis-cli -p 6379 -a yourpassword
```

### When to Rebuild

Code changes in `.py` files don't require a rebuild — the bind mount
(`.:/app`) makes them live immediately. Rebuild only when:

```bash
# After changing requirements/*.txt or Dockerfile
docker compose build

# Specific service only
docker compose build web

# Force full rebuild (no cache)
docker compose build --no-cache
```

---

## 🧪 Testing

### Run All Tests

```bash
# Always use the standalone command
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

**Why standalone and not merged with `docker-compose.yml`?**
The base file mounts named volumes (`postgres_data`, `redis_data`) at the same
paths the test file uses for tmpfs. Docker Compose cannot clear inherited volumes
during a file merge, which causes this error:

```
services.db.volumes[0]: target /var/lib/postgresql/data already mounted as services.db.tmpfs[0]
```

The test file is fully self-contained (different credentials, tmpfs, no Redis auth)
so standalone is both correct and simpler.

### CI Pipeline Command

```bash
# Builds fresh image, runs tests, exits with pytest's exit code
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test
```

> `--exit-code-from test` is essential for CI — without it `docker compose up`
> always exits 0 even when pytest fails, making your pipeline show green on failures.

### Run Specific Tests (in running dev container)

```bash
# All tests
docker compose exec web pytest -v

# Specific app
docker compose exec web pytest apps/authentication/tests/ -v

# Specific file
docker compose exec web pytest apps/authentication/tests/test_authentication.py -v

# Specific test
docker compose exec web pytest apps/authentication/tests/test_authentication.py::TestAuthentication::test_user_login -v

# Filter by keyword
docker compose exec web pytest -k "login" -v
```

### Coverage Reports

```bash
# Run via test compose (generates htmlcov/ in project root)
docker compose -f docker-compose.test.yml up --abort-on-container-exit

# Open coverage report
open htmlcov/index.html        # macOS
xdg-open htmlcov/index.html    # Linux
```

---

## 🚀 Production Deployment

### 1. Environment Setup

Create `.env.production` (never commit this file):

```bash
DJANGO_ENV=production
DJANGO_SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_urlsafe(50))">
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

POSTGRES_DB=authdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<very-strong-password>
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_PASSWORD=<very-strong-password>
CELERY_BROKER_URL=redis://:yourpassword@redis:6379/0
CELERY_RESULT_BACKEND=redis://:yourpassword@redis:6379/1

CORS_ALLOWED_ORIGINS=https://yourdomain.com
ACCOUNT_EMAIL_VERIFICATION=mandatory

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

GUNICORN_WORKERS=4
CELERY_CONCURRENCY=4
```

### 2. Deploy

```bash
# Use base file only — no override file in production
docker compose -f docker-compose.yml --env-file .env.production up -d --build

# Monitor startup
docker compose -f docker-compose.yml logs -f

# Create superuser
docker compose -f docker-compose.yml exec web python manage.py createsuperuser
```

### 3. Production Checklist

- [ ] `DJANGO_SECRET_KEY` is long, random, and unique per environment
- [ ] `DJANGO_DEBUG=False`
- [ ] `POSTGRES_PASSWORD` is strong
- [ ] `REDIS_PASSWORD` is strong and matches `CELERY_BROKER_URL`
- [ ] `ALLOWED_HOSTS` lists only your actual domains
- [ ] `ACCOUNT_EMAIL_VERIFICATION=mandatory`
- [ ] SSL/TLS configured (nginx or Traefik as reverse proxy)
- [ ] All `SECURE_*` and `*_COOKIE_SECURE` flags set to `True`
- [ ] Database backups scheduled
- [ ] `.env.production` not in version control

---

## 🔧 Troubleshooting

### Health Check First

```bash
curl http://localhost:8000/health/
# Expected: {"status": "ok", "checks": {"database": "ok", "cache": "ok"}}

# If degraded, it tells you which service is down:
# {"status": "degraded", "checks": {"database": "unavailable", "cache": "ok"}}
```

### Common Issues

#### Port already in use

```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

#### Redis authentication error (NOAUTH)

```bash
# Symptom: Celery can't connect, logs show "NOAUTH Authentication required"
# Cause: CELERY_BROKER_URL doesn't include REDIS_PASSWORD

# Check your .env — broker URL must include the password:
# redis://:yourpassword@redis:6379/0
#        ^^ note colon before password, no username

# Verify Redis itself is working:
docker compose exec redis redis-cli -a yourpassword ping
# Expected: PONG
```

#### Database connection error

```bash
docker compose ps           # check all services are healthy
docker compose logs db      # look for init errors
docker compose restart db
```

#### Module not found after adding a dependency

```bash
# Always rebuild after changing requirements files
docker compose build web
docker compose up -d web
```

#### Container exits immediately

```bash
docker compose logs web     # read the actual error

# Debug interactively
docker compose run --rm web bash
python manage.py check
```

#### Test volume conflict

```bash
# Error: target /data already mounted as services.redis.tmpfs[0]
# Cause: running test file merged with base file

# Fix: always run tests standalone
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Useful Debug Commands

```bash
# All container statuses and health
docker compose ps

# Follow all logs
docker compose logs -f

# Follow specific service, last 100 lines
docker compose logs -f --tail=100 web

# Shell into running container
docker compose exec web bash

# Check what env vars are actually set inside container
docker compose exec web env | sort

# Real-time CPU/memory usage
docker stats

# Full cleanup — removes containers, volumes, images
docker compose down -v --rmi all
docker compose build --no-cache
docker compose up
```

---

## 🎓 Advanced Usage

### Multi-Environment Setup

```bash
# Development (default — override auto-applied)
docker compose up

# Production-like without override
docker compose -f docker-compose.yml up

# Tests
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Personal Local Overrides

Create `docker-compose.local.yml` for your own machine-specific config (add to `.gitignore`):

```yaml
services:
  web:
    ports:
      - "8001:8000"   # use different port if 8000 is taken
    environment:
      DJANGO_LOG_LEVEL: DEBUG
```

Use it:
```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.local.yml up
```

### Scaling Celery Workers

```bash
# Run 3 celery worker containers
docker compose up -d --scale celery=3
```

### Using with Docker Swarm

```bash
docker swarm init
docker stack deploy -c docker-compose.yml auth_stack
docker stack services auth_stack
docker stack rm auth_stack
```

### Resource Limits

Already configured in `docker-compose.yml`:

| Service | Memory | CPU |
|---|---|---|
| web | 512MB | 1.0 core |
| celery | 512MB | 1.0 core |
| celery-beat | 256MB | 0.5 core |

Tune via `GUNICORN_WORKERS` and `CELERY_CONCURRENCY` in `.env`.

---

## 📊 Monitoring

```bash
# Real-time stats for all containers
docker stats

# Specific container
docker stats auth_web

# Export as table
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Save logs to file
docker compose logs > app.log
```

Log files rotate automatically — 10MB per file, 3 files kept per service.

---

## 🔐 Security Checklist

- [ ] `DJANGO_SECRET_KEY` is unique and not committed to git
- [ ] `POSTGRES_PASSWORD` is strong
- [ ] `REDIS_PASSWORD` is strong and matches `CELERY_BROKER_URL`
- [ ] Redis port not exposed in production (only in `docker-compose.override.yml`)
- [ ] PostgreSQL port not exposed in production (only in `docker-compose.override.yml`)
- [ ] `DJANGO_DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` restricted to your domains
- [ ] `ACCOUNT_EMAIL_VERIFICATION=mandatory` in production
- [ ] SSL/TLS enabled (nginx/Traefik in front)
- [ ] All `SECURE_*` flags `True` in production
- [ ] Running as non-root user (`django`) inside containers
- [ ] `.env` and `.env.production` in `.gitignore`

---

## 🎯 Quick Reference

```bash
# ── Development ─────────────────────────────────────────────────────────────
docker compose up -d                            # start dev environment
docker compose logs -f web                      # follow web logs
docker compose exec web bash                    # shell into web container
docker compose exec web python manage.py shell  # Django shell
docker compose down                             # stop services

# ── Testing ──────────────────────────────────────────────────────────────────
docker compose -f docker-compose.test.yml up --abort-on-container-exit

# ── Building ─────────────────────────────────────────────────────────────────
docker compose build                            # rebuild all images
docker compose up -d --force-recreate           # recreate without rebuild

# ── Cleanup ───────────────────────────────────────────────────────────────────
docker compose down -v                          # stop + remove volumes
docker system prune -a                          # clean ALL unused Docker resources
```

### Keyboard Shortcuts (in `docker compose logs -f`)

- `Ctrl+C` — stop tailing logs (containers keep running)

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [django-environ Documentation](https://django-environ.readthedocs.io/)

---

**Last Updated**: May 2026

**Docker**: 24.0+ | **Docker Compose**: 2.0+ | **Python**: 3.12 | **Django**: 5.x