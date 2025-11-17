# BrightLife Backend Testing Guide

## 🧪 Complete Testing Checklist

This guide walks through testing the backend API locally and preparing for production deployment.

---

## 1. Test API with Postman/Thunder Client

### Option A: Using Postman

1. **Import API Collection**
   ```bash
   # Open Postman → Import → Upload Files
   # Select: BrightLife_API_Collection.json
   ```

2. **Set Environment Variables**
   - Create new environment: "BrightLife Local"
   - Variables:
     ```
     base_url: http://localhost:8000
     access_token: (will be set after login)
     refresh_token: (will be set after login)
     ```

3. **Start Django Server**
   ```powershell
   cd c:\Drive_B\Bright_App\brightlife-django-backend
   venv\Scripts\activate
   python manage.py runserver
   ```

4. **Test Endpoints in Order**

   **Step 1: Create Superuser (if not done)**
   ```powershell
   python manage.py createsuperuser
   # Username: admin
   # Email: admin@brightlife.com
   # Password: (your secure password)
   ```

   **Step 2: Get JWT Token**
   - Send request: `Authentication → Login - Get JWT Token`
   - Body:
     ```json
     {
       "username": "admin",
       "password": "your_password"
     }
     ```
   - Response:
     ```json
     {
       "access": "eyJ0eXAiOiJKV1...",
       "refresh": "eyJ0eXAiOiJKV1..."
     }
     ```
   - Copy `access` token → Set as `access_token` variable

   **Step 3: Test User Endpoints**
   - `Users → Get Current User Profile` (should return admin details)
   - `Users → Register User (Public)` (create a test user)
   - `Users → List All Users (Admin)` (view all users)

   **Step 4: Test Token Refresh**
   - Wait for access token to expire (60 minutes default)
   - OR manually test: `Authentication → Refresh Token`

### Option B: Using Thunder Client (VS Code Extension)

1. **Install Extension**
   ```
   VS Code → Extensions → Search "Thunder Client" → Install
   ```

2. **Import Collection**
   - Thunder Client → Collections → Menu → Import
   - Select `BrightLife_API_Collection.json`

3. **Set Environment**
   - Thunder Client → Env → New Environment
   - Name: "Local"
   - Variables: Same as Postman above

4. **Run Tests** (same flow as Postman)

### Option C: Using cURL (Command Line)

```powershell
# 1. Get JWT Token
curl -X POST http://localhost:8000/api/auth/token/ `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"your_password\"}'

# 2. Get Current User (replace TOKEN with access token)
curl -X GET http://localhost:8000/api/v1/users/me/ `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

# 3. Register New User
curl -X POST http://localhost:8000/api/v1/users/ `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"SecurePass123!\",\"first_name\":\"Test\",\"last_name\":\"User\"}'
```

---

## 2. Connect Frontend to Backend

### Update Frontend Configuration

1. **Navigate to Frontend Directory**
   ```powershell
   cd c:\Drive_B\Bright_App\brightlife-typescript-app
   ```

2. **Create/Update `.env.local`**
   ```env
   # Disable mock API mode
   VITE_USE_MOCK_API=false
   
   # Point to local Django backend
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

3. **Start Both Servers**
   ```powershell
   # Terminal 1 - Backend
   cd c:\Drive_B\Bright_App\brightlife-django-backend
   venv\Scripts\activate
   python manage.py runserver

   # Terminal 2 - Frontend
   cd c:\Drive_B\Bright_App\brightlife-typescript-app
   npm run dev
   ```

4. **Test Integration**
   - Open browser: `http://localhost:5173`
   - Navigate to Registration/Membership form
   - Submit test application
   - Check browser console for API calls
   - Verify no CORS errors

### Troubleshooting CORS Issues

If you see CORS errors:

**Check Django settings.py:**
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',  # Vite dev server
]
```

**Restart Django server after changes**

---

## 3. Admin Panel Setup

### Access Django Admin

1. **Create Superuser** (if not done)
   ```powershell
   python manage.py createsuperuser
   ```

2. **Login to Admin**
   - URL: `http://localhost:8000/admin/`
   - Username: admin
   - Password: (your password)

3. **Verify Admin Interface**
   - Check "Users" section is visible
   - Verify you can view/edit users
   - Check "Groups" and "Permissions"

### Customize Admin Interface (Optional)

**apps/users/admin.py:**
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
```

---

## 4. Production Deployment Preparation

### Option 1: Railway Deployment (Recommended)

#### Prerequisites
```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

#### Deploy Backend

1. **Initialize Railway Project**
   ```powershell
   cd c:\Drive_B\Bright_App\brightlife-django-backend
   railway init
   ```

2. **Add PostgreSQL Database**
   ```powershell
   railway add
   # Select: PostgreSQL
   ```

3. **Set Environment Variables**
   ```powershell
   railway variables set SECRET_KEY="your-production-secret-key-here"
   railway variables set DEBUG="False"
   railway variables set ALLOWED_HOSTS="your-app.railway.app"
   railway variables set CORS_ALLOWED_ORIGINS="https://ya-shuvo30.github.io"
   ```

4. **Deploy**
   ```powershell
   railway up
   ```

5. **Run Migrations**
   ```powershell
   railway run python manage.py migrate
   railway run python manage.py createsuperuser
   ```

6. **Get Production URL**
   ```powershell
   railway status
   # Note the URL (e.g., https://brightlife-backend.railway.app)
   ```

### Option 2: Heroku Deployment

#### Prerequisites
```powershell
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli
heroku login
```

#### Deploy Backend

1. **Create Heroku App**
   ```powershell
   cd c:\Drive_B\Bright_App\brightlife-django-backend
   heroku create brightlife-backend
   ```

2. **Add PostgreSQL**
   ```powershell
   heroku addons:create heroku-postgresql:essential-0
   ```

3. **Set Environment Variables**
   ```powershell
   heroku config:set SECRET_KEY="your-production-secret-key"
   heroku config:set DEBUG="False"
   heroku config:set ALLOWED_HOSTS="brightlife-backend.herokuapp.com"
   heroku config:set CORS_ALLOWED_ORIGINS="https://ya-shuvo30.github.io"
   ```

4. **Create Procfile** (if not exists)
   ```
   web: gunicorn config.wsgi --log-file -
   ```

5. **Deploy**
   ```powershell
   git push heroku main
   ```

6. **Run Migrations**
   ```powershell
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### Option 3: Azure App Service

See `.github/workflows/deploy-azure.yml` for automated deployment.

---

## 5. Update Frontend for Production

### Update Frontend Environment

1. **Edit `.env.production` (create if doesn't exist)**
   ```env
   VITE_API_BASE_URL=https://brightlife-backend.railway.app/api
   VITE_USE_MOCK_API=false
   ```

2. **Update CORS in Backend**
   
   **Backend settings.py:**
   ```python
   CORS_ALLOWED_ORIGINS = [
       'http://localhost:5173',
       'https://ya-shuvo30.github.io',  # GitHub Pages
   ]
   ```

3. **Redeploy Backend** (to apply CORS changes)
   ```powershell
   # Railway
   railway up
   
   # OR Heroku
   git push heroku main
   ```

4. **Deploy Frontend**
   ```powershell
   cd c:\Drive_B\Bright_App\brightlife-typescript-app
   npm run build
   git add .
   git commit -m "Update API URL for production backend"
   git push origin main
   ```

---

## 6. Verification Checklist

### Local Testing
- [ ] Django server runs without errors
- [ ] Can login with superuser credentials
- [ ] JWT tokens are generated successfully
- [ ] User registration works (POST /api/v1/users/)
- [ ] Protected endpoints require authentication
- [ ] Token refresh works correctly
- [ ] Frontend connects to backend (no CORS errors)
- [ ] Form submissions reach backend
- [ ] Django admin is accessible

### Production Testing
- [ ] Backend deployed successfully
- [ ] PostgreSQL database connected
- [ ] Environment variables set correctly
- [ ] Migrations ran successfully
- [ ] Superuser created
- [ ] API endpoints accessible (https://your-backend.railway.app/api/)
- [ ] CORS allows frontend domain
- [ ] Frontend connects to production backend
- [ ] SSL/HTTPS enabled
- [ ] Static files served correctly

---

## 7. Common Issues & Solutions

### Issue: CORS Error in Browser
**Solution:**
```python
# Django settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'https://ya-shuvo30.github.io',
]
CORS_ALLOW_CREDENTIALS = True
```

### Issue: 500 Internal Server Error
**Solution:**
```powershell
# Check Django logs
railway logs  # Railway
heroku logs --tail  # Heroku

# Common causes:
# 1. Missing environment variables
# 2. Database not migrated
# 3. DEBUG=True in production (security issue)
```

### Issue: Static Files Not Loading
**Solution:**
```python
# settings.py
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Run:
python manage.py collectstatic --noinput
```

### Issue: Database Connection Failed
**Solution:**
```powershell
# Verify DATABASE_URL is set
railway variables  # Railway
heroku config  # Heroku

# Check format:
# postgres://user:password@host:5432/database
```

---

## 8. Next Steps After Successful Deployment

1. **Set up Monitoring**
   - Sentry for error tracking
   - Railway/Heroku dashboard for performance
   - Database monitoring

2. **Configure Backups**
   - Railway: Automatic PostgreSQL backups
   - Heroku: `heroku pg:backups:schedule`

3. **Set up CI/CD**
   - GitHub Actions already configured
   - Auto-deploy on push to main

4. **Add Custom Domain** (Optional)
   ```powershell
   # Railway
   railway domain

   # Heroku
   heroku domains:add api.brightlife-bd.com
   ```

5. **Security Hardening**
   - Rotate SECRET_KEY regularly
   - Enable rate limiting
   - Set up HTTPS redirect
   - Configure security headers

---

## 📞 Support

If you encounter issues:
1. Check Django logs: `railway logs` or `heroku logs --tail`
2. Verify environment variables are set
3. Test API with Postman/Thunder Client
4. Check CORS configuration
5. Verify database connection

**API Documentation:** `http://localhost:8000/api/schema/swagger-ui/`
