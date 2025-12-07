# BrightLife VPS Deployment - Quick Start Guide
# Server IP: 162.0.233.161

## Step-by-Step Deployment Instructions

### 1. Connect to VPS from Windows PowerShell

```powershell
ssh root@162.0.233.161
```
Enter your root password when prompted.

---

### 2. Download and Run Auto-Deploy Script

Once connected to VPS, run these commands:

```bash
# Download the deployment script
curl -o vps-deploy.sh https://raw.githubusercontent.com/yeasin-dev-me/Brightlife-Django-Backend/main/vps-deploy.sh

# Make it executable
chmod +x vps-deploy.sh

# Run the deployment
./vps-deploy.sh
```

**The script will automatically:**
- ✅ Update system packages
- ✅ Install Python 3.11, PostgreSQL, Nginx
- ✅ Create database and user
- ✅ Clone your GitHub repository
- ✅ Setup virtual environment
- ✅ Install all dependencies
- ✅ Configure environment variables
- ✅ Run migrations
- ✅ Collect static files
- ✅ Setup Gunicorn service
- ✅ Configure Nginx
- ✅ Enable firewall

---

### 3. OR Manual Deployment (if script fails)

#### A. Update System
```bash
apt update && apt upgrade -y
```

#### B. Install Dependencies
```bash
apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx git build-essential libpq-dev
```

#### C. Setup PostgreSQL
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE brightlife_db;
CREATE USER brightlife_user WITH PASSWORD 'BrightLife2025!Secure';
ALTER ROLE brightlife_user SET client_encoding TO 'utf8';
ALTER ROLE brightlife_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE brightlife_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE brightlife_db TO brightlife_user;
\q
```

#### D. Clone Repository
```bash
mkdir -p /var/www/brightlife
cd /var/www/brightlife
git clone https://github.com/yeasin-dev-me/Brightlife-Django-Backend.git .
```

#### E. Setup Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

#### F. Create .env File
```bash
nano .env
```

Paste this content:
```env
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=162.0.233.161,brightlife-bd.com,www.brightlife-bd.com

DATABASE_URL=postgres://brightlife_user:BrightLife2025!Secure@localhost:5432/brightlife_db

CORS_ALLOWED_ORIGINS=https://yeasin-dev-me.github.io

JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```
Save: `Ctrl+X`, `Y`, `Enter`

#### G. Run Migrations & Collect Static
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### H. Create Gunicorn Socket
```bash
nano /etc/systemd/system/gunicorn.socket
```

Paste:
```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

#### I. Create Gunicorn Service
```bash
nano /etc/systemd/system/gunicorn.service
```

Paste:
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

#### J. Set Permissions & Start
```bash
chown -R www-data:www-data /var/www/brightlife
chmod -R 755 /var/www/brightlife
systemctl start gunicorn.socket
systemctl enable gunicorn.socket
systemctl status gunicorn
```

#### K. Configure Nginx
```bash
nano /etc/nginx/sites-available/brightlife
```

Paste:
```nginx
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

Enable site:
```bash
ln -sf /etc/nginx/sites-available/brightlife /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### L. Configure Firewall
```bash
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw enable
```

---

### 4. Test Deployment

From your local machine:
```powershell
# Test API
curl http://162.0.233.161/api/

# Or open in browser
Start-Process "http://162.0.233.161/admin/"
```

---

### 5. Update Frontend Configuration

Update your frontend `.env` file:
```env
VITE_API_BASE_URL=http://162.0.233.161/api
VITE_USE_MOCK_API=false
```

---

### 6. Future Updates (From Local Machine)

Create `deploy-vps.ps1`:
```powershell
$SERVER = "root@162.0.233.161"
$APP_DIR = "/var/www/brightlife"

ssh $SERVER "cd $APP_DIR && git pull origin main && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && sudo systemctl restart gunicorn"

Write-Host "✅ Deployed to VPS!" -ForegroundColor Green
```

Run updates:
```powershell
.\deploy-vps.ps1
```

---

### 7. Useful Commands

**Check Services:**
```bash
systemctl status gunicorn
systemctl status nginx
systemctl status postgresql
```

**View Logs:**
```bash
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log
```

**Restart Services:**
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

### 8. Troubleshooting

**Gunicorn not starting:**
```bash
sudo journalctl -u gunicorn -n 50
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

**Nginx 502 Error:**
```bash
ls -l /run/gunicorn.sock
sudo chown www-data:www-data /run/gunicorn.sock
```

**Database connection error:**
```bash
sudo systemctl status postgresql
psql -U brightlife_user -d brightlife_db -h localhost
```

---

## Your VPS URLs

- **API Base:** http://162.0.233.161/api/
- **Admin Panel:** http://162.0.233.161/admin/
- **Swagger Docs:** http://162.0.233.161/api/schema/swagger-ui/
- **ReDoc:** http://162.0.233.161/api/schema/redoc/

---

## Next Steps (Optional)

1. **Setup Domain Name:**
   - Point your domain to 162.0.233.161
   - Update ALLOWED_HOSTS in .env
   - Update Nginx server_name

2. **Install SSL Certificate:**
```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

3. **Setup Monitoring:**
   - Install monitoring tools
   - Configure log rotation
   - Setup automated backups
