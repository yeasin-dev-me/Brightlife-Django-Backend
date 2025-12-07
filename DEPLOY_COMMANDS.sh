# Quick VPS Deployment - Copy & Paste Commands
# Server: root@162.0.233.161
# Password: w46s8K8UX4arLT6Fef

## STEP 1: Connect to VPS
# Open PowerShell and run:
ssh root@162.0.233.161
# Password: w46s8K8UX4arLT6Fef

## STEP 2: Once connected, copy and paste these commands one by one:

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx git build-essential libpq-dev curl

# Setup PostgreSQL database
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

# Create application directory
rm -rf /var/www/brightlife
mkdir -p /var/www/brightlife
cd /var/www/brightlife

# Clone repository
git clone https://github.com/yeasin-dev-me/Brightlife-Django-Backend.git .

# Setup Python virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create .env file
cat > .env << 'ENVEOF'
SECRET_KEY=django-insecure-brightlife-production-2025-change-in-real-production
DEBUG=False
ALLOWED_HOSTS=162.0.233.161,brightlife-bd.com,www.brightlife-bd.com

DATABASE_URL=postgres://brightlife_user:BrightLife2025!Secure@localhost:5432/brightlife_db

CORS_ALLOWED_ORIGINS=https://yeasin-dev-me.github.io,http://localhost:5173

JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
ENVEOF

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (will prompt for username, email, password)
python manage.py createsuperuser

# Create Gunicorn socket
cat > /etc/systemd/system/gunicorn.socket << 'SOCKEOF'
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
SOCKEOF

# Create Gunicorn service
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

# Set permissions
chown -R www-data:www-data /var/www/brightlife
chmod -R 755 /var/www/brightlife

# Start Gunicorn
systemctl daemon-reload
systemctl start gunicorn.socket
systemctl enable gunicorn.socket
systemctl status gunicorn

# Configure Nginx
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

# Enable Nginx site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/brightlife /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Configure firewall
ufw --force enable
ufw allow 'Nginx Full'
ufw allow OpenSSH

# Check services status
echo "==================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "==================================="
systemctl status gunicorn --no-pager | head -15
systemctl status nginx --no-pager | head -15

echo ""
echo "🌐 Your API is live at:"
echo "   http://162.0.233.161/api/"
echo ""
echo "🔧 Admin Panel:"
echo "   http://162.0.233.161/admin/"
echo ""
echo "📚 API Documentation:"
echo "   http://162.0.233.161/api/schema/swagger-ui/"
echo "==================================="
