# BrightLife VPS Deployment - Windows PowerShell
# Server: root@162.0.233.161
# This script will connect to VPS and deploy the application

$VPS_IP = "162.0.233.161"
$VPS_USER = "root"
$VPS_PASSWORD = "w46s8K8UX4arLT6Fef"
$APP_DIR = "/var/www/brightlife"

Write-Host "`n🚀 BrightLife Django Backend - VPS Deployment" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Function to run SSH commands
function Invoke-SSHCommand {
    param (
        [string]$Command
    )
    
    # Using plink for automated SSH (part of PuTTY)
    # Alternative: use ssh with sshpass or expect
    $sshCmd = "echo $VPS_PASSWORD | ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP '$Command'"
    Invoke-Expression $sshCmd
}

Write-Host "📡 Connecting to VPS: $VPS_IP" -ForegroundColor Yellow

# Create deployment script on VPS
$deployScript = @'
#!/bin/bash
set -e

echo "=================================="
echo "BrightLife Backend Auto-Deployment"
echo "=================================="

# Update System
echo "📦 Updating system..."
apt update && apt upgrade -y

# Install Dependencies
echo "📥 Installing dependencies..."
apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx git build-essential libpq-dev curl

# Setup PostgreSQL
echo "🗄️  Setting up database..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS brightlife_db;
DROP USER IF EXISTS brightlife_user;
CREATE DATABASE brightlife_db;
CREATE USER brightlife_user WITH PASSWORD 'BrightLife2025!Secure';
ALTER ROLE brightlife_user SET client_encoding TO 'utf8';
ALTER ROLE brightlife_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE brightlife_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE brightlife_db TO brightlife_user;
\q
EOF

# Create App Directory
echo "📁 Setting up application directory..."
rm -rf /var/www/brightlife
mkdir -p /var/www/brightlife
cd /var/www/brightlife

# Clone Repository
echo "📥 Cloning from GitHub..."
git clone https://github.com/ya-shuvo30/Brightlife-Django-Backend.git .

# Setup Python Environment
echo "🐍 Setting up Python environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create .env File
echo "⚙️  Creating environment file..."
cat > .env << 'ENVEOF'
SECRET_KEY=django-insecure-brightlife-production-key-change-this-in-production-2025
DEBUG=False
ALLOWED_HOSTS=162.0.233.161,brightlife-bd.com,www.brightlife-bd.com

DATABASE_URL=postgres://brightlife_user:BrightLife2025!Secure@localhost:5432/brightlife_db

CORS_ALLOWED_ORIGINS=https://ya-shuvo30.github.io,http://localhost:5173

JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
ENVEOF

# Run Django Setup
echo "🗄️  Running migrations..."
python manage.py migrate

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create Gunicorn Socket
echo "⚙️  Configuring Gunicorn..."
cat > /etc/systemd/system/gunicorn.socket << 'SOCKEOF'
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
SOCKEOF

# Create Gunicorn Service
cat > /etc/systemd/system/gunicorn.service << 'SVCEOF'
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/brightlife
Environment="PATH=/var/www/brightlife/venv/bin"
ExecStart=/var/www/brightlife/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
SVCEOF

# Set Permissions
echo "🔐 Setting permissions..."
chown -R www-data:www-data /var/www/brightlife
chmod -R 755 /var/www/brightlife

# Start Gunicorn
echo "🚀 Starting Gunicorn..."
systemctl daemon-reload
systemctl start gunicorn.socket
systemctl enable gunicorn.socket

# Configure Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/brightlife << 'NGXEOF'
server {
    listen 80;
    server_name 162.0.233.161;

    client_max_body_size 10M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/brightlife/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/brightlife/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, PATCH' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type, X-Requested-With' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}
NGXEOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/brightlife /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# Configure Firewall
echo "🔥 Configuring firewall..."
ufw --force enable
ufw allow 'Nginx Full'
ufw allow OpenSSH

echo ""
echo "✅ Deployment Complete!"
echo "=================================="
echo "🌐 API: http://162.0.233.161/api/"
echo "🔧 Admin: http://162.0.233.161/admin/"
echo "📚 Docs: http://162.0.233.161/api/schema/swagger-ui/"
echo "=================================="

# Check Status
systemctl status gunicorn --no-pager | head -10
systemctl status nginx --no-pager | head -10
'@

# Step 1: Upload deployment script
Write-Host "📤 Uploading deployment script..." -ForegroundColor Yellow
$deployScript | ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "cat > /root/deploy-brightlife.sh && chmod +x /root/deploy-brightlife.sh"

# Step 2: Execute deployment
Write-Host "🚀 Starting deployment..." -ForegroundColor Yellow
ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "bash /root/deploy-brightlife.sh"

Write-Host "`n🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Create superuser: ssh root@162.0.233.161 'cd /var/www/brightlife && source venv/bin/activate && python manage.py createsuperuser'" -ForegroundColor White
Write-Host "2. Test API: curl http://162.0.233.161/api/" -ForegroundColor White
Write-Host "3. Update frontend .env: VITE_API_BASE_URL=http://162.0.233.161/api" -ForegroundColor White
Write-Host "`n🌐 Open in browser:" -ForegroundColor Cyan
Write-Host "   Admin: http://162.0.233.161/admin/" -ForegroundColor White
Write-Host "   Docs:  http://162.0.233.161/api/schema/swagger-ui/" -ForegroundColor White
