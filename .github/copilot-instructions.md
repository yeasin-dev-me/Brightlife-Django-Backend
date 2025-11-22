# Development Guidelines

## Project Structure

```
apps/
├── users/          # User authentication & management
├── membership/     # Membership applications
└── core/           # Shared utilities
```

## Key Conventions

- Custom User model: `apps.users.User`
- API follows REST conventions
- JWT authentication for protected endpoints
- PostgreSQL database via environment config
- Separate serializers for read/write operations

## Quick Commands

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Start server
python manage.py runserver
```

## Environment Setup

Copy `.env.example` to `.env` and configure:
- Database credentials
- Secret key
- CORS origins
- Email settings (if needed)
UserCreateSerializer    # Registration (write, validation)
UserUpdateSerializer    # Profile updates (partial fields)
```

#### ViewSets (`apps/users/views.py`)
```python
class UserViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        # Dynamic serializer selection based on action
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        # Custom endpoint: GET /api/v1/users/me/
        return Response(self.get_serializer(request.user).data)
```

#### Permissions Strategy
- **Public endpoints**: `AllowAny()` (registration: `POST /api/v1/users/`)
- **Protected endpoints**: `IsAuthenticated()` (default for DRF)
- **Admin endpoints**: Override `get_permissions()` dynamically per action

### URL Patterns (`config/urls.py`)

#### API Structure:
```
/api/auth/token/           # JWT: Login (obtain token pair)
/api/auth/token/refresh/   # JWT: Refresh access token
/api/auth/token/verify/    # JWT: Verify token validity
/api/v1/users/             # User CRUD + 'me' endpoint
/api/schema/               # OpenAPI schema (drf-spectacular)
/api/schema/swagger-ui/    # Interactive API docs (dev only)
/api/schema/redoc/         # ReDoc API docs (dev only)
```

**Router registration** (`apps/users/urls.py`):
```python
router.register(r'users', UserViewSet, basename='user')
urlpatterns = router.urls
```

### Authentication & CORS

#### JWT Configuration (`settings.py`):
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),    # From .env
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=1440), # 24 hours
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

**Frontend authentication flow**:
1. POST `/api/auth/token/` with `username` + `password`
2. Response: `{ "access": "...", "refresh": "..." }`
3. Frontend stores tokens, sends `Authorization: Bearer <access>` header

#### CORS Setup:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',   # React dev server
    'http://localhost:5173',   # Vite dev server
    # Production: 'https://ya-shuvo30.github.io'
]
CORS_ALLOW_CREDENTIALS = True
```

### Error Handling
- DRF's default exception handlers return consistent JSON errors
- HTTP status codes: `400` (validation), `401` (unauthorized), `403` (forbidden), `404` (not found), `500` (server error)
- Custom exceptions: Define in `apps/core/exceptions.py` for business logic errors

### Environment & Settings

#### Environment Variables (`.env` via `python-decouple`):
```python
SECRET_KEY = config('SECRET_KEY', default='insecure-dev-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
DB_NAME = config('DB_NAME', default='brightlife_db')
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
```

**⚠️ Never commit `.env`** - use `.env.example` as template

## Common Commands

```bash
# Setup (Windows PowerShell)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# Development
python manage.py runserver              # http://localhost:8000
python manage.py runserver 0.0.0.0:8000 # Allow external connections
python manage.py makemigrations
python manage.py migrate

# Testing
python manage.py test                   # All tests
python manage.py test apps.users        # Specific app tests

# Shell
python manage.py shell                  # Django shell
python manage.py shell_plus             # Enhanced shell (django-extensions)

# Database
python manage.py dbshell                # PostgreSQL CLI
python manage.py dumpdata > backup.json # Export data
python manage.py loaddata backup.json   # Import data
```

## Key Dependencies
```python
djangorestframework           # API framework
djangorestframework-simplejwt # JWT authentication
psycopg2-binary              # PostgreSQL adapter
django-cors-headers          # CORS handling
django-filter                # Query filtering for DRF
drf-spectacular              # OpenAPI schema generation
python-decouple              # Environment variable management
whitenoise                   # Static file serving
django-extensions            # shell_plus, enhanced commands
django-debug-toolbar         # Dev debugging (enabled when DEBUG=True)
```

## Frontend Integration Points

### API Endpoints Used by Frontend
```python
# User Registration (Public)
POST /api/v1/users/
Body: { "username", "email", "password", "first_name", "last_name" }

# User Login
POST /api/auth/token/
Body: { "username", "password" }
Response: { "access": "jwt...", "refresh": "jwt..." }

# Get Current User Profile
GET /api/v1/users/me/
Headers: { "Authorization": "Bearer <access_token>" }

# Refresh Token
POST /api/auth/token/refresh/
Body: { "refresh": "jwt..." }
Response: { "access": "new_jwt..." }
```

### CORS Considerations
- Frontend runs on GitHub Pages: `https://ya-shuvo30.github.io`
- Development: `http://localhost:5173` (Vite)
- **Update CORS origins** in `.env` for production deployment

## GitHub Repository Management

### Current State
- Backend code exists in local directory: `c:\Drive_B\Bright_App\brightlife-django-backend`
- **No GitHub repository created yet** for backend (frontend repo: `ya-shuvo30/brightlife-typescript-app`)

### Recommended Actions

#### Option 1: Create Separate Backend Repo
```bash
cd brightlife-django-backend
git init
git add .
git commit -m "Initial Django REST API setup"
git remote add origin https://github.com/ya-shuvo30/brightlife-django-backend.git
git push -u origin main
```

**Advantages**: Independent versioning, separate deployment pipelines

#### Option 2: Monorepo (Recommended)
Merge both codebases into single repository:
```
brightlife-platform/
├── frontend/           # React TypeScript app
├── backend/            # Django REST API
├── .github/
│   └── workflows/
│       ├── frontend-deploy.yml
│       └── backend-deploy.yml
└── README.md
```

**Advantages**: Coordinated releases, shared documentation, atomic commits across stack

### Deployment Strategy

#### Local Development
1. Start PostgreSQL database (`localhost:5432`)
2. Run migrations: `python manage.py migrate`
3. Start backend: `python manage.py runserver`
4. Frontend connects to `http://localhost:8000/api`

#### Production Deployment Options

**Railway** (recommended for Django):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init
railway add  # Add PostgreSQL service
railway up   # Deploy
```

**Heroku**:
```bash
# Create Procfile
echo "web: gunicorn config.wsgi" > Procfile

# Create runtime.txt
echo "python-3.11.x" > runtime.txt

# Deploy
heroku create brightlife-backend
git push heroku main
heroku run python manage.py migrate
```

**Azure App Service** (enterprise option):
- Use Azure CLI or GitHub Actions workflow
- Configure PostgreSQL via Azure Database for PostgreSQL
- Set environment variables in Azure Portal

#### Environment Variables for Production
```env
SECRET_KEY=<generate-random-key>
DEBUG=False
ALLOWED_HOSTS=api.brightlife-bd.com,brightlife-backend.railway.app
DATABASE_URL=postgres://user:pass@host:5432/db  # Railway auto-sets this
CORS_ALLOWED_ORIGINS=https://ya-shuvo30.github.io
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

## GitHub Workflows (To Be Added)

### `.github/workflows/django-ci.yml` (CI/CD Pipeline)
```yaml
name: Django CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python manage.py test
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
```

## Common Pitfalls

1. **CORS errors**: Ensure frontend origin is in `CORS_ALLOWED_ORIGINS`
2. **JWT expiration**: Frontend must implement token refresh logic
3. **Database migrations**: Always review migrations before committing
4. **Static files**: Use WhiteNoise for serving (configured in `settings.py`)
5. **DEBUG=False in production**: Update `.env` for production deployment
6. **PostgreSQL password**: Use strong passwords, never commit `.env` file
7. **API versioning**: Use `/api/v1/` prefix for all endpoints (prepare for v2)

## Security Best Practices

- Rotate `SECRET_KEY` for production
- Use environment variables for all secrets
- Enable HTTPS in production (required for JWT)
- Set `SECURE_SSL_REDIRECT = True` when deployed
- Configure `ALLOWED_HOSTS` to specific domains only
- Use Django's built-in password validators
- Implement rate limiting (consider `django-ratelimit`)

## Monitoring & Logging (To Be Implemented)

- **Sentry**: Error tracking and performance monitoring
- **Datadog/New Relic**: APM for production
- **Django logging**: Configure in `settings.py` for structured logs
- **Database query monitoring**: Use Debug Toolbar in development
- `pillow` - Image handling (if needed)

## Testing Patterns
- Write tests in `tests/` directory within each app
- Use `APITestCase` from DRF for endpoint testing
- Test permissions, serializer validation, and business logic
- Use factories (factory_boy) for test data generation

## React Frontend Integration
- API consumed at `http://localhost:8000/api/v1/` (development)
- All endpoints return JSON with consistent structure:
  ```json
  {
    "data": {...},
    "message": "Success",
    "errors": null
  }
  ```
- Handle CORS preflight requests (OPTIONS)
- File uploads: use `multipart/form-data`, handle via `FileField` in serializers

## Security Checklist
- CSRF exemption for API views (DRF handles this)
- Validate all user input in serializers
- Use `select_related()` and `prefetch_related()` to prevent N+1 queries
- Implement rate limiting (`rest_framework.throttling`)
- Keep `DEBUG=False` in production

## When Adding New Features
1. Create models in `apps/{app_name}/models.py`
2. Create serializers in `serializers.py`
3. Create views/viewsets in `views.py`
4. Register routes in `urls.py`
5. Run migrations
6. Write tests
7. Update API documentation (if using drf-spectacular or similar)

## Database Queries
- Use ORM methods: `.filter()`, `.exclude()`, `.get()`, `.create()`, `.update()`
- Optimize with `.only()`, `.defer()`, `.select_related()`, `.prefetch_related()`
- Raw SQL only when ORM is insufficient (use `.raw()` or `cursor`)
- Always use parameterized queries to prevent SQL injection

## Code Style
- Follow PEP 8 (use `black` or `flake8`)
- Import order: stdlib → third-party → local
- Use meaningful variable names, avoid abbreviations
- Document complex business logic with docstrings
