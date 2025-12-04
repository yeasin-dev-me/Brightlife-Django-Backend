#!/bin/bash
# BrightLife Django Backend - Auto Deployment Script for VPS
# Server: 162.0.233.161
# Run this script on your VPS after SSH connection

set -e  # Exit on error

echo "=================================="
echo "BrightLife Backend Auto-Deployment"
echo "=================================="
echo ""

# Step 1: Update System
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Step 2: Install Dependencies
echo "📥 Installing Python, PostgreSQL, Nginx..."
apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib \
    nginx git build-essential libpq-dev curl

# Step 3: Setup PostgreSQL
echo "🗄️  Setting up PostgreSQL database..."
sudo -u postgres psql <<EOF
CREATE DATABASE brightlife_db;
CREATE USER brightlife_user WITH PASSWORD 'BrightLife2025!Secure';
ALTER ROLE brightlife_user SET client_encoding TO 'utf8';
ALTER ROLE brightlife_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE brightlife_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE brightlife_db TO brightlife_user;
\q
EOF

# Step 4: Create Application Directory
echo "📁 Creating application directory..."
mkdir -p /var/www/brightlife
cd /var/www/brightlife

# Step 5: Clone Repository
echo "📥 Cloning repository from GitHub..."
git clone https://github.com/ya-shuvo30/Brightlife-Django-Backend.git .

# Step 6: Setup Virtual Environment
echo "🐍 Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Step 7: Create Environment File
echo "⚙️  Creating .env file..."
cat > .env <<EOF
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=162.0.233.161,brightlife-bd.com,www.brightlife-bd.com

DATABASE_URL=postgres://brightlife_user:BrightLife2025!Secure@localhost:5432/brightlife_db

CORS_ALLOWED_ORIGINS=https://ya-shuvo30.github.io

JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
EOF

# Step 8: Run Migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Step 9: Collect Static Files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Step 10: Create Superuser (interactive)
echo "👤 Creating superuser..."
python manage.py createsuperuser

# Step 11: Setup Gunicorn Service
echo "⚙️  Configuring Gunicorn service..."
cat > /etc/systemd/system/gunicorn.socket <<EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

cat > /etc/systemd/system/gunicorn.service <<EOF
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/brightlife
Environment="PATH=/var/www/brightlife/venv/bin"
ExecStart=/var/www/brightlife/venv/bin/gunicorn \\
          --access-logfile - \\
          --workers 3 \\
          --bind unix:/run/gunicorn.sock \\
          config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Step 12: Set Permissions
echo "🔐 Setting permissions..."
chown -R www-data:www-data /var/www/brightlife
chmod -R 755 /var/www/brightlife

# Step 13: Start Gunicorn
echo "🚀 Starting Gunicorn..."
systemctl start gunicorn.socket
systemctl enable gunicorn.socket

# Step 14: Configure Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/brightlife <<EOF
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
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' 'https://ya-shuvo30.github.io' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        
        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }
}
EOF

ln -sf /etc/nginx/sites-available/brightlife /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Step 15: Configure Firewall
echo "🔥 Configuring firewall..."
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw --force enable

# Step 16: Final Status Check
echo ""
echo "✅ Deployment Complete!"
echo "=================================="
echo "🌐 API URL: http://162.0.233.161/api/"
echo "🔧 Admin: http://162.0.233.161/admin/"
echo "📚 Docs: http://162.0.233.161/api/schema/swagger-ui/"
echo ""
echo "Service Status:"
systemctl status gunicorn --no-pager
echo ""
systemctl status nginx --no-pager
echo ""
echo "⚠️  Next Steps:"
echo "1. Update your frontend VITE_API_BASE_URL to: http://162.0.233.161/api"
echo "2. (Optional) Setup domain and SSL certificate"
echo "3. Test API: curl http://162.0.233.161/api/"
echo "=================================="
