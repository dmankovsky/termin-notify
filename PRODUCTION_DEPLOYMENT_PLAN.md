# Production Deployment Plan - Termin-Notify

**Timeline**: Can be completed in 2-3 hours
**Cost**: ~€6/month ongoing

---

## ✅ Pre-Deployment Checklist

Before starting, ensure you have:

- [ ] Credit/Debit card (for Hetzner, ~€6/month)
- [ ] Gmail account with App Password ready
- [ ] 2-3 hours of uninterrupted time
- [ ] Local testing completed successfully
- [ ] GitHub repository accessible

---

## Phase 1: Get Gmail App Password (10 minutes)

### Step 1: Enable 2-Step Verification

1. Go to https://myaccount.google.com/security
2. Find "2-Step Verification"
3. If not enabled, click "Get Started" and follow steps
4. If already enabled, continue to Step 2

### Step 2: Create App Password

1. Go to https://myaccount.google.com/apppasswords
   - Or search "App passwords" in Google Account settings
2. Click "Select app" → Choose "Mail"
3. Click "Select device" → Choose "Other (Custom name)"
4. Enter name: "Termin-Notify Production"
5. Click "Generate"
6. **COPY the 16-character password** (format: xxxx xxxx xxxx xxxx)
7. **Save it securely** - you'll need it for deployment

**Example**: `abcd efgh ijkl mnop`

---

## Phase 2: Create Hetzner Account & Server (20 minutes)

### Step 1: Create Hetzner Account

1. Go to https://console.hetzner.cloud/
2. Click "Sign Up"
3. Fill in details:
   - Email
   - Password
   - Company name (can use your name or "Termin-Notify")
4. Verify email
5. Login to console

### Step 2: Add Payment Method

1. Go to "Billing" section
2. Add credit/debit card
3. No charge yet - only when server runs

### Step 3: Create Project

1. Click "New Project"
2. Name: `termin-notify-production`
3. Click "Create"

### Step 4: Create Server

**Configuration**:

| Setting | Value | Why |
|---------|-------|-----|
| **Location** | Nuremberg, Germany | GDPR compliance, low latency |
| **Image** | Ubuntu 22.04 | Stable, well-supported |
| **Type** | CX21 (Shared vCPU) | €5.83/month, sufficient for MVP |
| **Volume** | None | Not needed initially |
| **Network** | Default | Auto-created |
| **Firewall** | Create new (see below) | Security |
| **SSH Key** | Add yours (see below) | Secure access |
| **Name** | termin-notify-prod | Easy to identify |

**Firewall Rules** (Create new firewall named "termin-notify-firewall"):

| Direction | Protocol | Port | Source | Description |
|-----------|----------|------|--------|-------------|
| Inbound | TCP | 22 | 0.0.0.0/0 | SSH access |
| Inbound | TCP | 80 | 0.0.0.0/0 | HTTP |
| Inbound | TCP | 443 | 0.0.0.0/0 | HTTPS |
| Inbound | TCP | 8000 | 0.0.0.0/0 | API (temporary) |

**SSH Key Setup**:

1. Check if you have SSH key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # or
   cat ~/.ssh/id_rsa.pub
   ```

2. If you don't have one, generate:
   ```bash
   ssh-keygen -t ed25519 -C "your-email@gmail.com"
   # Press Enter for all prompts (use defaults)
   ```

3. Copy your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub | pbcopy
   ```

4. In Hetzner console:
   - Click "Add SSH Key"
   - Paste your public key
   - Name: "My Mac"
   - Save

**Final Step**: Click "Create & Buy now"

**Wait 1 minute** for server creation.

**Note the IP address** (e.g., 159.69.123.45) - you'll need this!

---

## Phase 3: Server Setup (30 minutes)

### Step 1: Connect to Server

```bash
# Replace YOUR_SERVER_IP with actual IP
ssh root@YOUR_SERVER_IP

# If prompted about fingerprint, type "yes"
```

You should now be connected to your server! 🎉

### Step 2: Update System

```bash
# Update package list
apt update

# Upgrade packages (this may take 5-10 minutes)
apt upgrade -y
```

### Step 3: Install Docker

```bash
# Install Docker using official script
curl -fsSL https://get.docker.com | sh

# Enable Docker to start on boot
systemctl enable docker

# Start Docker
systemctl start docker

# Verify installation
docker --version
```

Expected output: `Docker version 24.x.x`

### Step 4: Install Docker Compose

```bash
# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker-compose --version
```

Expected output: `docker-compose version 1.x.x`

### Step 5: Install Git

```bash
# Install Git
apt install git -y

# Verify installation
git --version
```

### Step 6: Setup UFW Firewall

```bash
# Install UFW
apt install ufw -y

# Allow SSH (IMPORTANT - do this first!)
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow API (temporary - will remove after Nginx setup)
ufw allow 8000/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

---

## Phase 4: Deploy Application (30 minutes)

### Step 1: Clone Repository

```bash
# Navigate to /opt
cd /opt

# Clone repository
git clone https://github.com/dmankovsky/termin-notify.git

# Navigate to project
cd termin-notify

# Verify files
ls -la
```

You should see all project files!

### Step 2: Create Production Environment File

```bash
# Create .env file from example
cp .env.example .env

# Edit with nano
nano .env
```

**Press `i` to enter INSERT mode, then edit these values**:

```env
# Database (CHANGE THE PASSWORD!)
DATABASE_URL=postgresql+asyncpg://termin_user:YOUR_STRONG_PASSWORD@postgres:5432/termin_notify
DATABASE_URL_SYNC=postgresql://termin_user:YOUR_STRONG_PASSWORD@postgres:5432/termin_notify

# Redis
REDIS_URL=redis://redis:6379/0

# Application (GENERATE NEW SECRET KEY!)
SECRET_KEY=YOUR_SECRET_KEY_HERE
ENVIRONMENT=production
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000

# Email (USE YOUR GMAIL APP PASSWORD!)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=noreply@termin-notify.de

# Stripe (leave empty for now)
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# Scraping
SCRAPE_INTERVAL_MINUTES=5
MAX_CONCURRENT_SCRAPES=3
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Notifications
MAX_NOTIFICATIONS_PER_USER_PER_DAY=50
NOTIFICATION_COOLDOWN_MINUTES=15
```

**Generate SECRET_KEY**:

Exit nano (`Esc`, then `:q!`), then:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and go back to editing .env:

```bash
nano .env
# Paste the secret key
```

**Save and exit**:
- Press `Esc`
- Type `:wq`
- Press `Enter`

### Step 3: Update docker-compose.yml

```bash
nano docker-compose.yml
```

Find the `postgres` section and change the password to match your .env:

```yaml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_USER: termin_user
    POSTGRES_PASSWORD: YOUR_STRONG_PASSWORD  # ← Same as in .env!
    POSTGRES_DB: termin_notify
```

Save and exit (Esc, :wq, Enter)

### Step 4: Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# This will:
# 1. Download Docker images (2-3 minutes)
# 2. Build application container (3-5 minutes)
# 3. Start postgres, redis, and app

# Wait for build to complete (be patient!)
```

### Step 5: Check Services Status

```bash
# Wait 15 seconds for everything to start
sleep 15

# Check status
docker-compose ps
```

**Expected output**: All services should show "Up" status

### Step 6: Initialize Database

```bash
# Initialize database with tables and seed data
docker-compose exec app python -m app.core.init_db
```

**Expected output**: "Database initialization completed!"

### Step 7: Verify Application

```bash
# Test health endpoint
curl http://localhost:8000/health
```

**Expected output**:
```json
{"status":"healthy","scheduler_running":true}
```

✅ **If you see this, your application is running!**

---

## Phase 5: Domain & SSL Setup (Optional - 30 minutes)

### If you have a domain (Recommended):

**Domain Setup**:

1. **Buy domain** (if you don't have one):
   - Namecheap.com, GoDaddy.com, or similar
   - Cost: ~€10/year
   - Suggested: `termin-notify.de` or `termin-notify.com`

2. **Configure DNS**:
   - Login to domain registrar
   - Go to DNS settings
   - Add A record:
     - **Host**: `@` (or leave blank)
     - **Value**: `YOUR_SERVER_IP`
     - **TTL**: 3600
   - Add A record for www:
     - **Host**: `www`
     - **Value**: `YOUR_SERVER_IP`
     - **TTL**: 3600
   - Save changes
   - Wait 5-10 minutes for DNS propagation

3. **Test DNS** (on your server):
   ```bash
   ping termin-notify.de
   # Should show your server IP
   ```

**Nginx & SSL Setup**:

```bash
# Install Nginx
apt install nginx -y

# Install Certbot for SSL
apt install certbot python3-certbot-nginx -y

# Create Nginx configuration
nano /etc/nginx/sites-available/termin-notify
```

Add this configuration (replace `termin-notify.de` with your domain):

```nginx
server {
    listen 80;
    server_name termin-notify.de www.termin-notify.de;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Save and exit.

```bash
# Enable site
ln -s /etc/nginx/sites-available/termin-notify /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# If OK, reload Nginx
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d termin-notify.de -d www.termin-notify.de
```

Follow prompts:
1. Enter email
2. Agree to terms (Y)
3. Share email? (N)
4. Redirect HTTP to HTTPS? (2 - Yes)

**Test**:
```bash
curl https://termin-notify.de/health
```

### If you DON'T have a domain yet:

You can use IP address temporarily:

**Access via**: `http://YOUR_SERVER_IP:8000`

Buy domain later and add SSL then.

---

## Phase 6: Post-Deployment Validation (15 minutes)

### Step 1: Test API Endpoints

From your Mac (replace IP/domain):

```bash
# Health check
curl http://YOUR_DOMAIN/health
# or
curl http://YOUR_SERVER_IP:8000/health

# List services
curl http://YOUR_DOMAIN/api/services/
```

### Step 2: Register First User

Open in browser: `http://YOUR_DOMAIN/docs` (or `http://YOUR_SERVER_IP:8000/docs`)

1. Register with your real email
2. Check if welcome email arrives
3. Login and get token
4. Create subscription
5. Verify dashboard

### Step 3: Check Monitoring is Running

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# View logs
cd /opt/termin-notify
docker-compose logs -f app

# Look for:
# - "Monitoring scheduler started"
# - "Starting monitoring cycle..."
# - Scraping logs every 5 minutes
```

Press `Ctrl+C` to exit logs.

### Step 4: Check Database

```bash
docker-compose exec app python manage.py stats
```

Should show:
- Users: 1+
- Services: 6
- Subscriptions: 1+

---

## Phase 7: Setup Automated Backups (10 minutes)

```bash
# Create backup directory
mkdir -p /opt/backups

# Create backup script
nano /opt/backup-termin-notify.sh
```

Add this content:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
cd /opt/termin-notify
docker-compose exec -T postgres pg_dump -U termin_user termin_notify | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup .env file
cp /opt/termin-notify/.env $BACKUP_DIR/env_$DATE.bak

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "env_*.bak" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Save and exit.

```bash
# Make executable
chmod +x /opt/backup-termin-notify.sh

# Test backup
/opt/backup-termin-notify.sh

# Add to cron (daily at 2 AM)
crontab -e
```

Add this line:
```
0 2 * * * /opt/backup-termin-notify.sh >> /var/log/termin-backup.log 2>&1
```

Save and exit.

---

## Phase 8: Monitoring Setup (10 minutes)

### Create Monitoring Script

```bash
nano /opt/monitor-termin-notify.sh
```

Add:

```bash
#!/bin/bash

# Check if services are running
cd /opt/termin-notify

SERVICES=$(docker-compose ps -q | wc -l)

if [ "$SERVICES" -lt 3 ]; then
    echo "WARNING: Some services are down!"
    docker-compose ps
    docker-compose up -d
    echo "Attempted restart at $(date)"
fi
```

```bash
chmod +x /opt/monitor-termin-notify.sh

# Add to cron (check every 5 minutes)
crontab -e
```

Add:
```
*/5 * * * * /opt/monitor-termin-notify.sh >> /var/log/termin-monitor.log 2>&1
```

---

## ✅ Deployment Complete Checklist

- [ ] Hetzner account created
- [ ] Server provisioned (CX21)
- [ ] Docker installed
- [ ] Repository cloned
- [ ] .env configured with real credentials
- [ ] docker-compose.yml updated with password
- [ ] Services started (postgres, redis, app)
- [ ] Database initialized
- [ ] Health check responds
- [ ] First user registered
- [ ] Welcome email received
- [ ] Monitoring scheduler running
- [ ] Backups configured
- [ ] Monitoring script created
- [ ] (Optional) Domain configured
- [ ] (Optional) SSL certificate installed

---

## 🎯 Your Production URLs

**Without Domain**:
- API: `http://YOUR_SERVER_IP:8000`
- Docs: `http://YOUR_SERVER_IP:8000/docs`
- Health: `http://YOUR_SERVER_IP:8000/health`

**With Domain & SSL**:
- API: `https://termin-notify.de`
- Docs: `https://termin-notify.de/docs`
- Health: `https://termin-notify.de/health`

---

## 📊 Monthly Costs

| Item | Cost |
|------|------|
| Hetzner CX21 | €5.83 |
| Domain (yearly/12) | €0.83 |
| **Total** | **€6.66/month** |

Email (Gmail): FREE (100 emails/day)
SSL Certificate (Let's Encrypt): FREE

---

## 🔧 Maintenance Commands

```bash
# View logs
docker-compose logs -f app

# Restart application
docker-compose restart app

# Restart all services
docker-compose restart

# Update code from GitHub
git pull
docker-compose up -d --build

# Database stats
docker-compose exec app python manage.py stats

# Manual backup
/opt/backup-termin-notify.sh

# Check disk space
df -h

# Check memory
free -h
```

---

## 🚨 Troubleshooting

### Services won't start

```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

### Database connection failed

```bash
# Check postgres password matches in both:
cat .env | grep DATABASE_URL
cat docker-compose.yml | grep POSTGRES_PASSWORD
```

### Email not sending

1. Verify Gmail App Password in .env
2. Check logs: `docker-compose logs app | grep -i email`
3. Test SMTP:
   ```bash
   docker-compose exec app python -c "from app.services.notification import NotificationService; import asyncio; ns = NotificationService(); asyncio.run(ns.send_email('test@example.com', 'Test', '<p>Test</p>'))"
   ```

### Out of disk space

```bash
# Clean up Docker
docker system prune -a

# Check large files
du -sh /opt/* | sort -h
```

---

## 📈 Next Steps After Deployment

1. ✅ Deployment complete
2. ⏳ Monitor for 24 hours (check logs, emails)
3. ⏳ Invite 5-10 beta testers
4. ⏳ Add legal pages (Impressum, Datenschutz, AGB)
5. ⏳ Setup Stripe (payments)
6. ⏳ Start marketing campaign

---

**Estimated Total Time**: 2-3 hours

**You're ready to deploy!** Follow this guide step-by-step and you'll have Termin-Notify live in production.

Good luck! 🚀
