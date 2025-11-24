#!/bin/bash
# Django Backend Deployment Script for CentOS/RHEL
# VPS IP: 162.0.233.161
# Run as: bash deploy-centos.sh

set -e  # Exit on any error

echo "========================================="
echo "Django Backend Deployment - CentOS/RHEL"
echo "========================================="

# Configuration
APP_DIR="/var/www/brightlife"
DB_NAME="brightlife_db"
DB_USER="brightlife_user"
DB_PASSWORD="BrightLife2025!Secure"
GITHUB_REPO="https://github.com/ya-shuvo30/Brightlife-Django-Backend.git"

echo ""
echo "Step 1/14: Updating system packages..."
sudo dnf update -y

echo ""
echo "Step 2/14: Installing system dependencies..."
sudo dnf install -y git python3.11 python3.11-pip python3.11-devel postgresql-server postgresql-contrib nginx

echo ""
echo "Step 3/14: Initializing PostgreSQL..."
if [ ! -f /var/lib/pgsql/data/PG_VERSION ]; then
    sudo postgresql-setup --initdb
fi
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo ""
echo "Step 4/14: Configuring PostgreSQL authentication..."
sudo sed -i 's/ident/md5/g' /var/lib/pgsql/data/pg_hba.conf
sudo systemctl restart postgresql

echo ""
echo "Step 5/14: Creating PostgreSQL database and user..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" || echo "User already exists"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo ""
echo "Step 6/14: Creating application directory..."
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

echo ""
echo "Step 7/14: Cloning repository from GitHub..."
if [ -d "$APP_DIR/.git" ]; then
    cd $APP_DIR
    git pull origin main
else
    git clone $GITHUB_REPO $APP_DIR
    cd $APP_DIR
fi

echo ""
echo "Step 8/14: Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

echo ""
echo "Step 9/14: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo ""
echo "Step 10/14: Creating .env file..."
cat > .env << EOF
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=162.0.233.161,localhost,127.0.0.1
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
CORS_ALLOWED_ORIGINS=https://ya-shuvo30.github.io,http://localhost:5173
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
EOF

echo ""
echo "Step 11/14: Running Django migrations..."
python manage.py migrate

echo ""
echo "Step 12/14: Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "Step 13/14: Setting up Gunicorn systemd service..."
sudo tee /etc/systemd/system/gunicorn.socket > /dev/null << EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

sudo tee /etc/systemd/system/gunicorn.service > /dev/null << EOF
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=nginx
Group=nginx
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/gunicorn \\
    --access-logfile - \\
    --workers 3 \\
    --bind unix:/run/gunicorn.sock \\
    config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

echo ""
echo "Step 14/14: Configuring Nginx..."
sudo tee /etc/nginx/conf.d/brightlife.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name 162.0.233.161;
    client_max_body_size 5M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/brightlife/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/brightlife/media/;
    }
    
    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo "Configuring firewall..."
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload

echo ""
echo "Setting SELinux to permissive mode..."
sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config

echo ""
echo "Setting correct permissions..."
sudo chown -R nginx:nginx $APP_DIR
sudo chmod -R 755 $APP_DIR

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Your Django API is now live at:"
echo "  http://162.0.233.161/api/"
echo ""
echo "Next steps:"
echo "1. Create a superuser:"
echo "   cd $APP_DIR"
echo "   source venv/bin/activate"
echo "   python manage.py createsuperuser"
echo ""
echo "2. Access admin panel:"
echo "   http://162.0.233.161/admin/"
echo ""
echo "3. View API documentation:"
echo "   http://162.0.233.161/api/schema/swagger-ui/"
echo ""
echo "4. Update frontend .env:"
echo "   VITE_API_BASE_URL=http://162.0.233.161/api"
echo "========================================="
