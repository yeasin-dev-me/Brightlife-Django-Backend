# BrightLife Django Backend - Quick Start

## ✅ Installation Complete!

All dependencies have been installed and the project structure is ready.

## 📋 What's Been Set Up

- ✅ Django 5.2.8 with Django REST Framework
- ✅ PostgreSQL database configuration
- ✅ JWT authentication (djangorestframework-simplejwt)
- ✅ CORS headers for React frontend
- ✅ API documentation (Swagger/ReDoc)
- ✅ Custom User model with extended fields
- ✅ User management endpoints
- ✅ Development tools (black, flake8, django-extensions)

## 🚀 Next Steps

### 1. Setup PostgreSQL Database

Make sure PostgreSQL is installed and running, then create the database:

```bash
# Using psql
psql -U postgres
CREATE DATABASE brightlife_db;
\q

# Or using PowerShell (if psql is in PATH)
psql -U postgres -c "CREATE DATABASE brightlife_db;"
```

### 2. Update Environment Variables

Edit `.env` file and update database credentials if needed:
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT

### 3. Run Migrations

```bash
C:/Drive_B/Bright_App/brightlife-django-backend/.venv/Scripts/python.exe manage.py makemigrations
C:/Drive_B/Bright_App/brightlife-django-backend/.venv/Scripts/python.exe manage.py migrate
```

### 4. Create Superuser

```bash
C:/Drive_B/Bright_App/brightlife-django-backend/.venv/Scripts/python.exe manage.py createsuperuser
```

### 5. Run Development Server

```bash
C:/Drive_B/Bright_App/brightlife-django-backend/.venv/Scripts/python.exe manage.py runserver
```

Server will run at: `http://localhost:8000`

## 📚 API Endpoints

### Authentication
- `POST /api/auth/token/` - Get JWT tokens (login)
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/token/verify/` - Verify token

### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Register new user (public)
- `GET /api/v1/users/me/` - Get current user
- `GET /api/v1/users/{id}/` - Get user details
- `PATCH /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Deactivate user

### Documentation
- `http://localhost:8000/api/schema/swagger-ui/` - Swagger UI
- `http://localhost:8000/api/schema/redoc/` - ReDoc
- `http://localhost:8000/admin/` - Django Admin

## 🧪 Testing the API

### Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Login to get JWT token
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### Get current user (with token)
```bash
curl -X GET http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔧 Development Commands

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Django shell
python manage.py shell

# Format code
black .
isort .

# Run tests
python manage.py test
```

## 📁 Project Structure

```
brightlife-django-backend/
├── .venv/                 # Virtual environment
├── config/                # Django settings
│   ├── settings.py       # Main settings (REST, CORS, JWT, DB)
│   ├── urls.py           # URL routing
│   └── wsgi.py
├── apps/
│   ├── users/            # User management app
│   │   ├── models.py    # Custom User model
│   │   ├── serializers.py # User serializers
│   │   ├── views.py     # User ViewSet
│   │   └── urls.py      # User endpoints
│   └── core/            # Shared utilities
├── .env                  # Environment variables
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
├── manage.py
└── README.md
```

## 🎯 React Frontend Integration

The API is configured to work with React:
- CORS enabled for `http://localhost:3000` and `http://localhost:5173`
- All endpoints return JSON
- JWT tokens in Authorization header: `Bearer YOUR_TOKEN`
- File uploads supported via multipart/form-data

## ⚠️ Important Notes

1. **Database**: PostgreSQL must be running before starting the server
2. **Migrations**: Run migrations after any model changes
3. **Security**: Change SECRET_KEY in production
4. **CORS**: Add production frontend URL to CORS_ALLOWED_ORIGINS
5. **Static Files**: Run `python manage.py collectstatic` before deployment

## 📖 Documentation

See `.github/copilot-instructions.md` for AI agent guidelines and development conventions.

## 🆘 Troubleshooting

### Database Connection Error
- Check PostgreSQL is running
- Verify database credentials in `.env`
- Ensure database `brightlife_db` exists

### Module Not Found
- Activate virtual environment: `.\.venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Migration Errors
- Delete migration files (except `__init__.py`)
- Delete database and recreate
- Run `makemigrations` and `migrate` again

---

**Ready to start coding!** 🚀
