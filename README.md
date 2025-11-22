# BrightLife Backend API

REST API for the BrightLife health membership management system built with Django REST Framework.

## Overview

This backend serves the BrightLife membership platform, handling user registration, membership applications, payment proof submissions, document uploads, and administrative workflows.

**Frontend Repository**: [brightlife-typescript-app](https://github.com/ya-shuvo30/brightlife-typescript-app)

## Features

- ✅ **User Management**: JWT-based authentication with custom user model
- ✅ **Membership Applications**: Complete membership workflow with nominees and medical records
- ✅ **Payment Proof System**: Upload and verify payment screenshots with auto-generated receipts
- ✅ **Document Uploads**: Photo, age proof, and nominee ID document handling
- ✅ **Admin Interface**: Color-coded badges, bulk actions, and verification workflows
- ✅ **API Documentation**: Auto-generated Swagger and ReDoc

## Tech Stack

- Django 5.0.14 with Django REST Framework 3.16.1
- PostgreSQL 15 (production) / SQLite (development)
- JWT authentication (Simple JWT)
- Docker & Docker Compose support
- WhiteNoise for static files
- CORS configured for frontend integration

## Quick Start

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

## 🚀 Deployment

This project includes automated CI/CD pipelines for multiple deployment platforms.

### Quick Deploy

**Railway** (Recommended):
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

**Heroku**:
```bash
heroku create brightlife-backend
git push heroku main
```

**Docker**:
```bash
docker-compose up --build
```

📖 **Full deployment guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

### CI/CD Workflows

- **Django CI/CD**: Automated testing, linting, and security scans
- **Railway Deploy**: Auto-deploy to Railway on push to `main`
- **Heroku Deploy**: Manual deployment workflow
- **Docker Build**: Container image builds

All workflows are in `.github/workflows/` directory.

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

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT token pair (login)
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/token/verify/` - Verify token validity

### Users
- `POST /api/v1/users/` - Register new user
- `GET /api/v1/users/me/` - Get current user profile
- `PUT /api/v1/users/me/` - Update current user profile

### Membership Applications
- `POST /api/v1/membership/applications/` - Submit membership application
- `GET /api/v1/membership/applications/` - List applications (admin)
- `GET /api/v1/membership/applications/{id}/` - Get application details

### Payment Proof (NEW)
- `POST /api/v1/payment/proof/` - Submit payment proof with screenshot
- `GET /api/v1/payment/proof/{transaction_id}/` - Check payment status
- **Admin endpoints:**
  - `GET /api/v1/payment/admin/payment-proofs/` - List all payment proofs
  - `POST /api/v1/payment/admin/payment-proofs/{id}/verify/` - Verify payment
  - `POST /api/v1/payment/admin/payment-proofs/{id}/reject/` - Reject payment

**Payment Response includes auto-generated receipt data for frontend modal/print**

## API Documentation

- **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

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

## Deployment

See deployment documentation for production setup with:
- Gunicorn WSGI server
- Nginx reverse proxy
- PostgreSQL database
- Static file serving with WhiteNoise

## Contributing

1. Create feature branch
2. Make changes
3. Write/update tests
4. Run code formatters (black, isort)
5. Submit pull request

## License

[Your License Here]
