# BrightLife Django Backend

Django REST Framework backend API for the BrightLife application.

## Tech Stack

- **Django 5.x** - Web framework
- **Django REST Framework** - REST API toolkit
- **PostgreSQL** - Database
- **JWT** - Authentication
- **React** - Frontend (separate repository)

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

```
brightlife-django-backend/
├── config/              # Project configuration
├── apps/               # Django applications
│   ├── users/         # User management
│   ├── api/           # API versioning
│   └── core/          # Shared utilities
├── static/            # Static files
├── media/             # User uploads
└── manage.py
```

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
