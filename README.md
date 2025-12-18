# BrightLife Backend API

REST API for the BrightLife health membership management system built with Django REST Framework.

## 🌐 Live Deployment

| Environment | URL |
|-------------|-----|
| **Frontend** | https://www.brightlifebd.com |
| **Backend API** | https://api.brightlifebd.com |
| **Admin Panel** | https://api.brightlifebd.com/admin/ |
| **API Documentation** | https://api.brightlifebd.com/api/schema/swagger-ui/ |
| **ReDoc** | https://api.brightlifebd.com/api/schema/redoc/ |

## Overview

This backend serves the BrightLife membership platform, handling user registration, membership applications, payment proof submissions, document uploads, and administrative workflows.

**Frontend Repository**: [brightlife-typescript-app](https://github.com/yeasin-dev-me/brightlife-typescript-app)

## Features

- ✅ **User Management**: JWT-based authentication with custom user model
- ✅ **Membership Applications**: Complete membership workflow with nominees and medical records
- ✅ **Payment Proof System**: Upload and verify payment screenshots with auto-generated receipts
- ✅ **Document Uploads**: Photo, age proof, and nominee ID document handling
- ✅ **Admin Interface**: Color-coded badges, bulk actions, and verification workflows
- ✅ **API Documentation**: Auto-generated Swagger and ReDoc
- ✅ **Production Deployment**: Live on VPS with SSL/TLS (Let's Encrypt)

## Tech Stack

- Django 5.0.14 with Django REST Framework 3.16.1
- PostgreSQL 15 (production)
- JWT authentication (Simple JWT)
- Gunicorn WSGI Server
- Nginx Reverse Proxy
- Let's Encrypt SSL Certificate
- Docker & Docker Compose support
- WhiteNoise for static files
- CORS configured for frontend integration

---

## 🔗 Live API Endpoints

### Admin Panel
| Description | URL |
|-------------|-----|
| Django Admin Dashboard | https://api.brightlifebd.com/admin/ |
| Users Management | https://api.brightlifebd.com/admin/users/user/ |
| Membership Applications | https://api.brightlifebd.com/admin/membership/membershipapplication/ |
| Nominees | https://api.brightlifebd.com/admin/membership/nominee/ |
| Medical Records | https://api.brightlifebd.com/admin/membership/medicalrecord/ |
| Payment Proofs | https://api.brightlifebd.com/admin/payment/paymentproof/ |

### Authentication API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | https://api.brightlifebd.com/api/auth/token/ | Login (obtain JWT tokens) |
| POST | https://api.brightlifebd.com/api/auth/token/refresh/ | Refresh access token |
| POST | https://api.brightlifebd.com/api/auth/token/verify/ | Verify token validity |

### Users API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | https://api.brightlifebd.com/api/v1/users/ | Register new user |
| GET | https://api.brightlifebd.com/api/v1/users/ | List all users (admin) |
| GET | https://api.brightlifebd.com/api/v1/users/me/ | Get current user profile |
| PUT | https://api.brightlifebd.com/api/v1/users/me/ | Update current user profile |

### Membership API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | https://api.brightlifebd.com/api/v1/membership/applications/ | Submit membership application |
| GET | https://api.brightlifebd.com/api/v1/membership/applications/ | List applications |
| GET | https://api.brightlifebd.com/api/v1/membership/applications/{id}/ | Get application details |
| PATCH | https://api.brightlifebd.com/api/v1/membership/applications/{id}/ | Update application |

### Payment API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | https://api.brightlifebd.com/api/v1/payment/proof/ | Submit payment proof |
| GET | https://api.brightlifebd.com/api/v1/payment/proof/{transaction_id}/ | Check payment status |
| GET | https://api.brightlifebd.com/api/v1/payment/admin/payment-proofs/ | List all proofs (admin) |
| POST | https://api.brightlifebd.com/api/v1/payment/admin/payment-proofs/{id}/verify/ | Verify payment |
| POST | https://api.brightlifebd.com/api/v1/payment/admin/payment-proofs/{id}/reject/ | Reject payment |

### Agent Onboarding API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | https://api.brightlifebd.com/api/v1/agents/applications/ | Submit agent onboarding form (public, throttled) |
| GET | https://api.brightlifebd.com/api/v1/agents/applications/ | List applications (staff only) |
| GET | https://api.brightlifebd.com/api/v1/agents/applications/{id}/ | Review application detail (staff only) |
| PATCH | https://api.brightlifebd.com/api/v1/agents/applications/{id}/ | Update status, notes, reviewer metadata (staff only) |

### Agent Onboarding Security & Observability
- **Authorization Rules**: `POST` submissions stay open to prospective agents, while `list`, `retrieve`, and moderation actions inherit `IsAdminUser`, ensuring only staff can access or mutate stored records.
- **API Hardening**: Submissions are rate-limited through DRF's scoped throttling (tuned via `AGENT_ONBOARDING_THROTTLE`) and every payload must confirm `agreeTerms`, sanitize phone numbers, and passes serializer-level validation.
- **Observability**: The `agents` logger captures successful submissions, validation failures, request IPs, and user agents so operations teams can trend onboarding volume and detect abuse.

### API Documentation
| Description | URL |
|-------------|-----|
| Swagger UI (Interactive) | https://api.brightlifebd.com/api/schema/swagger-ui/ |
| ReDoc (Clean Layout) | https://api.brightlifebd.com/api/schema/redoc/ |
| OpenAPI JSON Schema | https://api.brightlifebd.com/api/schema/ |

---

## 🖥️ VPS Server Information

### Server Details
| Property | Value |
|----------|-------|
| IP Address | `162.0.233.161` |
| Domain | `api.brightlifebd.com` |
| OS | AlmaLinux (CentOS/RHEL) |
| Web Server | Nginx 1.20.1 |
| App Server | Gunicorn 23.0.0 |
| Database | PostgreSQL 15 |
| Python | 3.11 |
| SSL | Let's Encrypt (valid until Feb 22, 2026) |

### Application Paths
| Path | Description |
|------|-------------|
| `/var/www/brightlife` | Application root |
| `/var/www/brightlife/venv` | Python virtual environment |
| `/var/www/brightlife/.env` | Environment configuration |
| `/var/www/brightlife/staticfiles` | Collected static files |
| `/var/www/brightlife/media` | User uploaded files |

### SSH Access
```bash
ssh root@162.0.233.161
```

### Service Management Commands
```bash
# Gunicorn (Django App Server)
sudo systemctl status gunicorn
sudo systemctl restart gunicorn
sudo journalctl -u gunicorn -f  # View logs

# Nginx (Web Server)
sudo systemctl status nginx
sudo systemctl restart nginx
sudo nginx -t  # Test configuration

# PostgreSQL
sudo systemctl status postgresql
sudo systemctl restart postgresql

# Django Management
cd /var/www/brightlife
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Update Deployment
```bash
# SSH into server
ssh root@162.0.233.161

# Navigate to project
cd /var/www/brightlife
source venv/bin/activate

# Pull latest code
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn
```

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip & virtualenv

### Installation

1. **Clone and navigate to project**
   ```bash
   cd brightlife-django-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env  # macOS/Linux
   ```
   Edit `.env` and update database credentials and secret key.

5. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE brightlife_db;
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

API will be available at `http://localhost:8000/api/v1/`

### PostgreSQL via Docker Compose (Preferred for Local Dev)

```bash
# Start only the database container
docker compose up -d db

# Apply migrations against the running container
C:/Drive_B/Bright_App/.venv/Scripts/python.exe manage.py migrate

# (Optional) create a superuser for admin logins
C:/Drive_B/Bright_App/.venv/Scripts/python.exe manage.py createsuperuser

# Run the API once the DB is healthy
C:/Drive_B/Bright_App/.venv/Scripts/python.exe manage.py runserver
```

Your `.env` can either keep `DATABASE_URL` or use the discrete `DB_*` variables. When using Docker, set `DB_HOST=db` so Django connects to the containerized Postgres instance defined in [docker-compose.yml](docker-compose.yml).

#### Smoke Test the Connection

```bash
C:/Drive_B/Bright_App/.venv/Scripts/python.exe manage.py dbshell
```

If `dbshell` opens without errors, the application can reach PostgreSQL.

### Deployment Readiness Checklist

1. **Lock environment variables**: update `.env`/platform secrets with `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and either `DATABASE_URL` or all `DB_*` values (see [.env.example](.env.example)).
2. **Run framework checks**:
   ```bash
   C:/Drive_B/Bright_App/.venv/Scripts/python.exe manage.py check --deploy
   ```
3. **Collect assets & migrate**:
   ```bash
   C:/Drive_B/Bright_App/.venv/Scripts/python.exe manage.py collectstatic --noinput
   C:/Drive_B/Bright_App/.venv/Scripts/python.exe manage.py migrate
   ```
4. **Create admin credentials**: `python manage.py createsuperuser` (run via SSH/CLI on the target environment).
5. **Smoke test with Gunicorn/Docker**:
   ```bash
   # Gunicorn locally
   gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application

   # Or Docker image
   docker build -t brightlife-backend:latest .
   docker run --rm -p 8000:8000 --env-file .env brightlife-backend:latest
   ```
6. **Review deployment docs**: [DEPLOYMENT.md](DEPLOYMENT.md) for CI/CD options or [DEPLOYMENT_SSH.md](DEPLOYMENT_SSH.md) for manual VPS steps.

---

## 🚀 Deployment

This project supports multiple deployment methods.

### Production (Current - VPS)

The application is currently deployed on a VPS with:
- **Nginx** as reverse proxy with SSL
- **Gunicorn** as WSGI server
- **PostgreSQL** as database
- **Let's Encrypt** for SSL certificates
- **systemd** for service management

📖 **Complete SSH deployment guide**: [DEPLOYMENT_SSH.md](./DEPLOYMENT_SSH.md)

### Alternative Deploy Options

**1. Railway** (Easiest):
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

**2. Heroku**:
```bash
heroku create brightlife-backend
git push heroku main
```

**3. Docker Compose**:
```bash
docker-compose up --build
```

📖 **Platform-specific guides**: See [DEPLOYMENT.md](./DEPLOYMENT.md) for Railway, Heroku, Azure instructions.

### CI/CD Workflows

- **Django CI/CD**: Automated testing, linting, and security scans
- **Railway Deploy**: Auto-deploy to Railway on push to `main`
- **Heroku Deploy**: Manual deployment workflow
- **Docker Build**: Container image builds

All workflows are in `.github/workflows/` directory.

---

## Development

### Common Commands

```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Open Django shell
python manage.py shell

# Code formatting
black .
isort .
flake8
```

### Project Structure

```plaintext
brightlife-django-backend/
├── config/              # Project configuration
│   ├── settings.py     # Django settings
│   ├── urls.py         # Main URL routing
│   └── wsgi.py         # WSGI application
├── apps/               # Django applications
│   ├── users/         # User authentication & management
│   ├── membership/    # Membership applications with nominees & medical records
│   ├── payment/       # Payment proof submissions & verification
│   └── core/          # Shared utilities
├── media/             # User uploads (photos, documents, payment screenshots)
├── staticfiles/       # Collected static files for production
├── docker-compose.yml # Docker orchestration
├── Dockerfile         # Container configuration
├── requirements.txt   # Python dependencies
└── manage.py
```

---

## 🗄️ Database

### PostgreSQL Connection (Production)
```
Host: localhost
Port: 5432
Database: brightlife_db
User: brightlife_user
```

### Access Database
```bash
# Via SSH
ssh root@162.0.233.161
psql -U brightlife_user -d brightlife_db -h localhost

# Via Django Shell
cd /var/www/brightlife
source venv/bin/activate
python manage.py shell
```

### Key Tables
| Table | Description |
|-------|-------------|
| `users_user` | User accounts and authentication |
| `membership_membershipapplication` | Membership applications |
| `membership_nominee` | Application nominees |
| `membership_medicalrecord` | Medical history records |
| `payment_paymentproof` | Payment screenshots and verification |

---

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 🔐 Security

### Production Environment Variables
```env
SECRET_KEY=<secure-random-key>
DEBUG=False
ALLOWED_HOSTS=api.brightlifebd.com,162.0.233.161
CORS_ALLOWED_ORIGINS=https://www.brightlifebd.com,https://brightlifebd.com
DATABASE_URL=postgresql://user:pass@localhost:5432/brightlife_db
```

### SSL Certificate
- **Provider**: Let's Encrypt (Certbot)
- **Expiry**: February 22, 2026
- **Auto-Renewal**: Enabled via systemd timer

---

## 📊 Monitoring

### View Logs
```bash
# Gunicorn logs
sudo journalctl -u gunicorn -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Check Services Status
```bash
sudo systemctl status gunicorn nginx postgresql
```

---

## Contributing

1. Create feature branch
2. Make changes
3. Write/update tests
4. Run code formatters (black, isort)
5. Submit pull request

---

## 📞 Support

- **Repository Issues**: [GitHub Issues](https://github.com/yeasin-dev-me/brightlife-django-backend/issues)
- **Email**: 123yeasinarafat@gmail.com

---

## License

[Your License Here]

---

**Last Updated**: November 24, 2025
**Maintainer**: Ya Shuvo