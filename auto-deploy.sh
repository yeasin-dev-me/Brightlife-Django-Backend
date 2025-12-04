#!/bin/bash
# BrightLife Django Backend - Complete Deployment Script
# Run this entire script on your VPS after logging in

set -e  # Exit on any error

echo "🚀 Starting BrightLife Backend Deployment..."
echo "============================================"

# 1. Update System
echo ""
echo "📦 Step 1/12: Updating system packages..."
apt update && apt upgrade -y

# 2. Install Dependencies
echo ""
echo "📥 Step 2/12: Installing Python, PostgreSQL, Nginx, Git..."
apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx git build-essential libpq-dev curl

# 3. Setup PostgreSQL
echo ""
echo "🗄️  Step 3/12: Setting up PostgreSQL database..."
sudo -u postgres psql << 'EOF'
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
echo "✅ Database created successfully!"

# 4. Create App Directory
echo ""
echo "📁 Step 4/12: Creating application directory..."
rm -rf /var/www/brightlife
mkdir -p /var/www/brightlife
cd /var/www/brightlife

# 5. Clone Repository
echo ""
echo "📥 Step 5/12: Cloning repository from GitHub..."
git clone https://github.com/ya-shuvo30/Brightlife-Django-Backend.git .
echo "✅ Repository cloned!"

# 6. Setup Virtual Environment
echo ""
echo "🐍 Step 6/12: Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
echo "✅ Python environment ready!"

# 7. Create Environment File
echo ""
echo "⚙️  Step 7/12: Creating .env configuration..."
cat > .env << 'ENVEOF'
SECRET_KEY=django-insecure-brightlife-production-2025-change-in-real-production
DEBUG=False
ALLOWED_HOSTS=162.0.233.161,brightlife-bd.com,www.brightlife-bd.com

DATABASE_URL=postgres://brightlife_user:BrightLife2025!Secure@localhost:5432/brightlife_db

CORS_ALLOWED_ORIGINS=https://ya-shuvo30.github.io,http://localhost:5173

JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
ENVEOF
echo "✅ Environment configured!"

# 8. Run Migrations
echo ""
echo "🗄️  Step 8/12: Running database migrations..."
python manage.py migrate
echo "✅ Migrations complete!"

# 9. Collect Static Files
echo ""
echo "📁 Step 9/12: Collecting static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected!"

# 10. Setup Gunicorn
echo ""
echo "⚙️  Step 10/12: Configuring Gunicorn service..."

cat > /etc/systemd/system/gunicorn.socket << 'SOCKEOF'
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
SOCKEOF

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

chown -R www-data:www-data /var/www/brightlife
chmod -R 755 /var/www/brightlife

systemctl daemon-reload
systemctl start gunicorn.socket
systemctl enable gunicorn.socket
echo "✅ Gunicorn configured and started!"

# 11. Configure Nginx
echo ""
echo "🌐 Step 11/12: Configuring Nginx web server..."

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
echo "✅ Nginx configured and restarted!"

# 12. Configure Firewall
echo ""
echo "🔥 Step 12/12: Configuring firewall..."
ufw --force enable
ufw allow 'Nginx Full'
ufw allow OpenSSH
echo "✅ Firewall configured!"

# Final Status
echo ""
echo "============================================"
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "============================================"
echo ""
echo "📊 Service Status:"
systemctl status gunicorn --no-pager | head -10
echo ""
systemctl status nginx --no-pager | head -10
echo ""
echo "============================================"
echo "🌐 YOUR API IS LIVE AT:"
echo "   http://162.0.233.161/api/"
echo ""
echo "🔧 ADMIN PANEL:"
echo "   http://162.0.233.161/admin/"
echo ""
echo "📚 API DOCUMENTATION:"
echo "   http://162.0.233.161/api/schema/swagger-ui/"
echo "   http://162.0.233.161/api/schema/redoc/"
echo "============================================"
echo ""
echo "📝 NEXT STEPS:"
echo "1. Create Django superuser:"
echo "   cd /var/www/brightlife"
echo "   source venv/bin/activate"
echo "   python manage.py createsuperuser"
echo ""
echo "2. Update your frontend .env:"
echo "   VITE_API_BASE_URL=http://162.0.233.161/api"
echo ""
echo "3. Test the API:"
echo "   curl http://162.0.233.161/api/"
echo "============================================"
