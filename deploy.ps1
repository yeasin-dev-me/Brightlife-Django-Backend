# BrightLife Backend - SSH Deploy Script
# Usage: .\deploy.ps1

param(
    [string]$Server = "username@your-server-ip",
    [string]$AppDir = "/var/www/brightlife",
    [string]$Branch = "main"
)

Write-Host "`n🚀 BrightLife Backend Deployment" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Step 1: Pull latest code
Write-Host "📥 Pulling latest code from GitHub..." -ForegroundColor Yellow
ssh $Server "cd $AppDir && git pull origin $Branch"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git pull failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
ssh $Server "cd $AppDir && source venv/bin/activate && pip install -r requirements.txt --quiet"

# Step 3: Run migrations
Write-Host "`n🗄️  Running database migrations..." -ForegroundColor Yellow
ssh $Server "cd $AppDir && source venv/bin/activate && python manage.py migrate"

# Step 4: Collect static files
Write-Host "`n📁 Collecting static files..." -ForegroundColor Yellow
ssh $Server "cd $AppDir && source venv/bin/activate && python manage.py collectstatic --noinput"

# Step 5: Restart Gunicorn
Write-Host "`n🔄 Restarting Gunicorn..." -ForegroundColor Yellow
ssh $Server "sudo systemctl restart gunicorn"

# Step 6: Check status
Write-Host "`n✅ Checking service status..." -ForegroundColor Yellow
ssh $Server "sudo systemctl is-active gunicorn"

Write-Host "`n🎉 Deployment complete!" -ForegroundColor Green
Write-Host "Visit: https://your-domain.com/api/`n" -ForegroundColor Green
