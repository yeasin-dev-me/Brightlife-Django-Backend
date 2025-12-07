# SSH Deployment Guide

Complete guide for deploying BrightLife Django Backend to a remote server via SSH.

## Prerequisites

- Remote server (Ubuntu 20.04+ / Debian)
- SSH access to server
- Domain name (optional but recommended)
- Server with at least 1GB RAM

## 1. Generate SSH Key (Local Machine)

### Windows PowerShell:
```powershell
# Generate SSH key pair
ssh-keygen -t ed25519 -C "your-email@example.com"

# Save to default location: C:\Users\ADMIN\.ssh\id_ed25519
# Press Enter for no passphrase or set a secure one

# View your public key
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
```

### Copy Public Key to Server:
```powershell
# Method 1: Manual copy
type $env:USERPROFILE\.ssh\id_ed25519.pub

# Method 2: ssh-copy-id (if available)
ssh-copy-id username@your-server-ip
```

## 2. Initial Server Setup

### Connect to Server:
```bash
ssh username@your-server-ip
# or with key:
ssh -i C:\Users\ADMIN\.ssh\id_ed25519 username@your-server-ip
```

### Update System:
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Required Packages:
```bash
# Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Nginx
sudo apt install -y nginx

# Git
sudo apt install -y git

# System utilities
sudo apt install -y build-essential libpq-dev
```

## 3. Setup PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE brightlife_db;
CREATE USER brightlife_user WITH PASSWORD 'your-secure-password';
ALTER ROLE brightlife_user SET client_encoding TO 'utf8';
ALTER ROLE brightlife_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE brightlife_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE brightlife_db TO brightlife_user;
\q
```

## 4. Deploy Django Application

### Create App Directory:
```bash
sudo mkdir -p /var/www/brightlife
sudo chown $USER:$USER /var/www/brightlife
cd /var/www/brightlife
```

### Clone Repository:
```bash
# Option 1: HTTPS (will prompt for credentials)
git clone https://github.com/yeasin-dev-me/Brightlife-Django-Backend.git .

# Option 2: SSH (requires GitHub SSH key setup)
git clone git@github.com:yeasin-dev-me/Brightlife-Django-Backend.git .
```

### Setup Python Virtual Environment:
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### Create Environment File:
```bash
nano .env
```

Add the following:
```env
SECRET_KEY=your-super-secret-key-generate-new-one
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

DATABASE_URL=postgres://brightlife_user:your-secure-password@localhost:5432/brightlife_db

CORS_ALLOWED_ORIGINS=https://yeasin-dev-me.github.io,https://your-domain.com

JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Optional: Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Run Migrations and Collect Static Files:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 5. Setup Gunicorn Service

### Create Gunicorn Socket:
```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

### Create Gunicorn Service:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
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
```

### Set Permissions:
```bash
sudo chown -R www-data:www-data /var/www/brightlife
sudo chmod -R 755 /var/www/brightlife
```

### Start Gunicorn:
```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn.socket
```

### Test Socket:
```bash
sudo systemctl status gunicorn
curl --unix-socket /run/gunicorn.sock localhost
```

## 6. Configure Nginx

### Create Nginx Configuration:
```bash
sudo nano /etc/nginx/sites-available/brightlife
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

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
        add_header 'Access-Control-Allow-Origin' 'https://yeasin-dev-me.github.io' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}
```

### Enable Site:
```bash
sudo ln -s /etc/nginx/sites-available/brightlife /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Allow Nginx Through Firewall:
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## 7. SSL Certificate (Let's Encrypt)

### Install Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain Certificate:
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Auto-renewal:
```bash
sudo systemctl status certbot.timer
```

## 8. Deploy Updates via SSH

### From Local Machine (PowerShell):

Create deployment script `deploy.ps1`:
```powershell
# deploy.ps1
$SERVER = "username@your-server-ip"
$APP_DIR = "/var/www/brightlife"

Write-Host "🚀 Deploying to production..." -ForegroundColor Green

# Pull latest code
ssh $SERVER "cd $APP_DIR && git pull origin main"

# Install dependencies
ssh $SERVER "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt"

# Run migrations
ssh $SERVER "cd $APP_DIR && source venv/bin/activate && python manage.py migrate"

# Collect static files
ssh $SERVER "cd $APP_DIR && source venv/bin/activate && python manage.py collectstatic --noinput"

# Restart Gunicorn
ssh $SERVER "sudo systemctl restart gunicorn"

Write-Host "✅ Deployment complete!" -ForegroundColor Green
```

### Run Deployment:
```powershell
.\deploy.ps1
```

### Or Manual SSH Commands:
```powershell
# Connect to server
ssh username@your-server-ip

# Navigate to app
cd /var/www/brightlife

# Pull changes
git pull origin main

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## 9. Monitoring & Logs

### Check Gunicorn Status:
```bash
sudo systemctl status gunicorn
```

### View Logs:
```bash
# Gunicorn logs
sudo journalctl -u gunicorn

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Django logs (if configured)
tail -f /var/www/brightlife/logs/django.log
```

### Restart Services:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## 10. Backup Strategy

### Database Backup Script:
```bash
#!/bin/bash
# /var/www/brightlife/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/www/brightlife/backups"
mkdir -p $BACKUP_DIR

# Backup database
pg_dump brightlife_db > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/brightlife/media

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Schedule Backups (Cron):
```bash
crontab -e

# Add daily backup at 2 AM
0 2 * * * /var/www/brightlife/backup.sh
```

## 11. SSH Configuration Tips

### SSH Config File (Local - Windows):

Create: `C:\Users\ADMIN\.ssh\config`
```
Host brightlife-prod
    HostName your-server-ip
    User username
    IdentityFile C:\Users\ADMIN\.ssh\id_ed25519
    Port 22
```

Now you can connect with:
```powershell
ssh brightlife-prod
```

### Security Hardening:

On server `/etc/ssh/sshd_config`:
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 2222  # Change default port
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

## 12. Troubleshooting

### Gunicorn Not Starting:
```bash
sudo journalctl -u gunicorn -n 50
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

### Nginx 502 Bad Gateway:
```bash
# Check socket
sudo systemctl status gunicorn.socket
ls -l /run/gunicorn.sock

# Check permissions
sudo chown www-data:www-data /run/gunicorn.sock
```

### Database Connection Issues:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U brightlife_user -d brightlife_db -h localhost
```

### Static Files Not Loading:
```bash
# Collect static
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R www-data:www-data /var/www/brightlife/staticfiles
```

## 13. Production Checklist

- [ ] `DEBUG=False` in `.env`
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured
- [ ] Database credentials secure
- [ ] SSL certificate installed
- [ ] Firewall configured (UFW)
- [ ] Backups scheduled
- [ ] Monitoring setup
- [ ] Logs rotation configured
- [ ] CORS properly configured
- [ ] Static files served correctly
- [ ] Media uploads working

## Quick Reference

**Connect to Server:**
```powershell
ssh username@your-server-ip
```

**Deploy Updates:**
```bash
cd /var/www/brightlife
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

**Check Status:**
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql
```

**View Logs:**
```bash
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log
```
