# Backend Deployment Guide

## 🚀 CI/CD Workflows Overview

This repository includes multiple GitHub Actions workflows for automated testing and deployment:

### 1. **Django CI/CD Pipeline** (`.github/workflows/django-ci.yml`)
Runs on every push and pull request to `main` and `develop` branches.

**Jobs:**
- **Test**: Runs Django tests with PostgreSQL
- **Lint**: Code quality checks (Black, isort, Flake8)
- **Security**: Dependency and code security scanning

**Status Badge:** Add to README.md
```markdown
![Django CI](https://github.com/yeasin-dev-me/Brightlife-Django-Backend/workflows/Django%20CI%2FCD%20Pipeline/badge.svg)
```

### 2. **Railway Deployment** (`.github/workflows/deploy-railway.yml`)
Automatically deploys to Railway on push to `main` branch.

**Requirements:**
- Railway account and project
- `RAILWAY_TOKEN` secret configured in GitHub

### 3. **Heroku Deployment** (`.github/workflows/deploy-heroku.yml`)
Manual deployment to Heroku via workflow dispatch.

**Requirements:**
- Heroku account and app
- GitHub secrets: `HEROKU_API_KEY`, `HEROKU_APP_NAME`, `HEROKU_EMAIL`

### 4. **Docker Image Build** (`.github/workflows/docker-build.yml`)
Builds and pushes Docker images to GitHub Container Registry.

---

## 📋 Deployment Setup Instructions

### Option 1: Railway (Recommended)

#### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

#### Step 2: Login and Initialize
```bash
cd brightlife-django-backend
railway login
railway init
```

#### Step 3: Add PostgreSQL Database
```bash
railway add
# Select: PostgreSQL
```

#### Step 4: Configure Environment Variables
```bash
railway variables set SECRET_KEY="your-production-secret-key-here"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="your-app.railway.app"
railway variables set CORS_ALLOWED_ORIGINS="https://yeasin-dev-me.github.io"
```

#### Step 5: Deploy
```bash
railway up
```

#### Step 6: Run Migrations
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

#### Step 7: Get Railway Token for GitHub Actions
```bash
railway whoami --token
# Copy the token and add to GitHub Secrets as RAILWAY_TOKEN
```

---

### Option 2: Heroku

#### Step 1: Install Heroku CLI
```bash
# Windows (PowerShell)
curl https://cli-assets.heroku.com/install-windows-x64.exe -o heroku-installer.exe
.\heroku-installer.exe
```

#### Step 2: Login and Create App
```bash
heroku login
heroku create brightlife-backend
```

#### Step 3: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:mini
```

#### Step 4: Configure Environment Variables
```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG="False"
heroku config:set ALLOWED_HOSTS="brightlife-backend.herokuapp.com"
heroku config:set CORS_ALLOWED_ORIGINS="https://yeasin-dev-me.github.io"
```

#### Step 5: Deploy
```bash
git push heroku main
```

#### Step 6: Run Migrations
```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### Step 7: Configure GitHub Secrets
Add these secrets in GitHub repository settings:
- `HEROKU_API_KEY`: Get from Heroku account settings
- `HEROKU_APP_NAME`: `brightlife-backend`
- `HEROKU_EMAIL`: Your Heroku account email

---

### Option 3: Docker Deployment

#### Local Development with Docker
```bash
# Build and run with docker-compose
docker-compose up --build

# Access at http://localhost:8000
```

#### Production Deployment
```bash
# Build image
docker build -t brightlife-backend:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  -e DATABASE_URL="postgres://user:pass@host:5432/db" \
  -e DEBUG="False" \
  brightlife-backend:latest
```

---

## 🔐 GitHub Secrets Configuration

Go to: `https://github.com/yeasin-dev-me/Brightlife-Django-Backend/settings/secrets/actions`

### Required Secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `RAILWAY_TOKEN` | Railway authentication token | Get from `railway whoami --token` |
| `HEROKU_API_KEY` | Heroku API key | From Heroku account settings |
| `HEROKU_APP_NAME` | Heroku app name | `brightlife-backend` |
| `HEROKU_EMAIL` | Heroku account email | `your-email@example.com` |

---

## 🔄 CI/CD Workflow Triggers

### Automatic Triggers:
- **Push to `main`**: Runs CI tests + Railway deployment
- **Push to `develop`**: Runs CI tests only
- **Pull Requests**: Runs CI tests only

### Manual Triggers:
- **Railway Deploy**: Go to Actions → Deploy to Railway → Run workflow
- **Heroku Deploy**: Go to Actions → Deploy to Heroku → Run workflow

---

## 📊 Monitoring Deployment

### Check CI Status
```bash
# View workflow runs
gh run list --repo yeasin-dev-me/Brightlife-Django-Backend

# View specific run
gh run view <run-id>
```

### Check Deployed App
- **Railway**: `https://your-project.railway.app/api/schema/swagger-ui/`
- **Heroku**: `https://brightlife-backend.herokuapp.com/api/schema/swagger-ui/`

---

## 🔧 Post-Deployment Tasks

### 1. Update Frontend Environment
Edit `brightlife-typescript-app/.env`:
```env
VITE_API_BASE_URL=https://your-backend.railway.app/api
VITE_USE_MOCK_API=false
```

### 2. Configure Production CORS
Update backend `.env` or Railway variables:
```env
CORS_ALLOWED_ORIGINS=https://yeasin-dev-me.github.io
```

### 3. Create Superuser
```bash
# Railway
railway run python manage.py createsuperuser

# Heroku
heroku run python manage.py createsuperuser
```

### 4. Test API Endpoints
```bash
# Health check
curl https://your-backend.railway.app/api/schema/

# Get JWT token
curl -X POST https://your-backend.railway.app/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'
```

---

## 🐛 Troubleshooting

### Build Failures
```bash
# Check workflow logs
gh run view --log

# Re-run failed jobs
gh run rerun <run-id>
```

### Database Migration Issues
```bash
# Railway
railway run python manage.py showmigrations
railway run python manage.py migrate --fake-initial

# Heroku
heroku run python manage.py showmigrations
heroku run python manage.py migrate --fake-initial
```

### Static Files Not Loading
```bash
# Railway
railway run python manage.py collectstatic --noinput

# Heroku
heroku run python manage.py collectstatic --noinput
```

---

## 📈 Next Steps

1. ✅ Push workflow files to GitHub
2. ⬜ Configure GitHub Secrets
3. ⬜ Deploy to Railway/Heroku
4. ⬜ Update frontend API URL
5. ⬜ Test authentication flow
6. ⬜ Set up monitoring (Sentry)
7. ⬜ Configure custom domain (optional)

---

## 🔗 Useful Links

- **Repository**: https://github.com/yeasin-dev-me/Brightlife-Django-Backend
- **Frontend**: https://github.com/yeasin-dev-me/brightlife-typescript-app
- **Railway Docs**: https://docs.railway.app/
- **Heroku Docs**: https://devcenter.heroku.com/
- **Django Deployment**: https://docs.djangoproject.com/en/stable/howto/deployment/
