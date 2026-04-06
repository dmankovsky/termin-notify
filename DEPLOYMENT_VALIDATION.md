# Termin-Notify - Deployment Validation Guide

**Complete step-by-step guide to validate locally and deploy to production**

---

## Phase 1: Local Validation (Required - 30 minutes)

Before deploying to production, we need to ensure everything works locally.

### Step 1: Start Docker Desktop

Make sure Docker Desktop is running on your Mac.

```bash
# Check Docker is running
docker ps
```

If not running, start Docker Desktop from Applications.

### Step 2: Start Local Services

```bash
cd /Users/dmankovskyi/GitHub/Private/termin-notify

# Start all services
docker-compose up -d

# Wait 10 seconds for services to start
sleep 10

# Check services are running
docker-compose ps
```

**Expected output**: postgres, redis, and app should all be "Up"

### Step 3: Initialize Database

```bash
# Initialize database with tables and seed data
docker-compose exec app python -m app.core.init_db
```

**Expected output**: "Database initialization completed!"

### Step 4: Create Test User

```bash
# Run test setup
docker-compose exec app python test_setup.py
```

**Expected output**: Test user credentials and scraper test results

### Step 5: Access API Documentation

```bash
# Open API docs in browser
open http://localhost:8000/docs
```

**You should see**: Interactive API documentation (Swagger UI)

### Step 6: Test API Endpoints

**Test in the Swagger UI** (http://localhost:8000/docs):

1. **Register a new user**:
   - POST /api/auth/register
   - Click "Try it out"
   - Enter:
     ```json
     {
       "email": "your-real-email@gmail.com",
       "password": "test123456",
       "full_name": "Your Name"
     }
     ```
   - Execute
   - **Expected**: 200 response with user details

2. **Login**:
   - POST /api/auth/login
   - Click "Try it out"
   - Enter username (email) and password
   - Execute
   - **Expected**: Access token returned
   - **Copy the access_token** for next steps

3. **Authorize** (click green "Authorize" button at top):
   - Enter: `Bearer YOUR_ACCESS_TOKEN`
   - Click "Authorize"

4. **List available services**:
   - GET /api/services/
   - Execute
   - **Expected**: List of Berlin, Munich, Hamburg, Frankfurt services

5. **Subscribe to a service**:
   - POST /api/subscriptions/
   - Enter:
     ```json
     {
       "service_id": 1,
       "notify_email": true
     }
     ```
   - Execute
   - **Expected**: Subscription created

6. **View dashboard**:
   - GET /api/users/dashboard
   - Execute
   - **Expected**: User stats and active subscriptions

### Step 7: Check Logs

```bash
# View application logs
docker-compose logs -f app

# Press Ctrl+C to stop
```

**Look for**:
- "Monitoring scheduler started"
- "Starting monitoring cycle..."
- No error messages

### Step 8: Test Database

```bash
# Connect to database
docker-compose exec postgres psql -U termin_user -d termin_notify

# Run queries
SELECT count(*) FROM users;
SELECT count(*) FROM appointment_services;
SELECT count(*) FROM subscriptions;

# Exit
\q
```

**Expected**: At least 1 user, 4+ services

---

## ✅ Local Validation Checklist

Before proceeding to deployment, verify:

- [ ] Docker services start successfully
- [ ] Database initializes without errors
- [ ] Test user can be created
- [ ] Login works and returns token
- [ ] API endpoints respond correctly
- [ ] Subscriptions can be created
- [ ] Dashboard displays data
- [ ] Logs show monitoring is running
- [ ] No critical errors in logs

**If all checks pass → Proceed to deployment**

---

## Phase 2: Pre-Deployment Checklist (10 minutes)

### Email Configuration

You need working SMTP credentials for production. **Choose one**:

#### Option A: Gmail (Free, Easiest)

1. Go to Google Account → Security
2. Enable 2-Step Verification (if not already)
3. Go to "App passwords" (search in settings)
4. Generate password for "Mail"
5. Copy 16-character password

**You'll need**:
- SMTP_HOST: smtp.gmail.com
- SMTP_PORT: 587
- SMTP_USER: your-gmail@gmail.com
- SMTP_PASSWORD: 16-character-app-password

#### Option B: SendGrid (Better for scale)

1. Create account: https://sendgrid.com (free tier: 100 emails/day)
2. Create API key
3. Verify sender email

**You'll need**:
- SMTP_HOST: smtp.sendgrid.net
- SMTP_PORT: 587
- SMTP_USER: apikey
- SMTP_PASSWORD: your-sendgrid-api-key

### Stripe Account (Optional for now)

You can launch without payments and add later:
1. Create account: https://stripe.com
2. Get test keys (start with test mode)
3. Can upgrade to live keys later

### Domain (Optional but recommended)

- Buy domain: namecheap.com, godaddy.com (~€10/year)
- Recommended: termin-notify.de or termin-notify.com
- Can deploy with IP address first, add domain later

---

## Phase 3: Deploy to Hetzner VPS (1-2 hours)

### Step 1: Create Hetzner Account & Server

1. **Create account**: https://console.hetzner.cloud/

2. **Create project**: "termin-notify-production"

3. **Create server**:
   - **Location**: Nuremberg (Germany - better for GDPR)
   - **Image**: Ubuntu 22.04
   - **Type**: CX21 (2 vCPU, 4GB RAM, 40GB SSD) - €5.83/month
   - **SSH Key**: Add your SSH key (or create password)
   - **Name**: termin-notify-prod

4. **Wait 1 minute** for server to be created

5. **Note the IP address** (e.g., 159.69.123.45)

### Step 2: Initial Server Setup

```bash
# SSH into server (replace IP with yours)
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
apt install docker-compose -y

# Install Git
apt install git -y

# Verify installations
docker --version
docker-compose --version
git --version
```

### Step 3: Clone Repository

```bash
# Clone your repository
cd /opt
git clone https://github.com/dmankovsky/termin-notify.git
cd termin-notify

# Verify files
ls -la
```

### Step 4: Configure Environment

```bash
# Create production .env file
cp .env.example .env
nano .env
```

**Edit these values** (press `i` to edit, `Esc` then `:wq` to save):

```env
# Database
DATABASE_URL=postgresql+asyncpg://termin_user:CHANGE_THIS_PASSWORD@postgres:5432/termin_notify
DATABASE_URL_SYNC=postgresql://termin_user:CHANGE_THIS_PASSWORD@postgres:5432/termin_notify

# Redis
REDIS_URL=redis://redis:6379/0

# Application
SECRET_KEY=GENERATE_RANDOM_STRING_HERE
ENVIRONMENT=production
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000

# Email (use your credentials from pre-deployment)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=noreply@termin-notify.de

# Scraping
SCRAPE_INTERVAL_MINUTES=5
MAX_CONCURRENT_SCRAPES=3
```

**Generate secure SECRET_KEY**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as SECRET_KEY value.

### Step 5: Update docker-compose.yml for Production

```bash
nano docker-compose.yml
```

Find the postgres section and **change the password**:
```yaml
postgres:
  environment:
    POSTGRES_USER: termin_user
    POSTGRES_PASSWORD: CHANGE_THIS_PASSWORD  # ← Change this!
    POSTGRES_DB: termin_notify
```

Make sure it matches the password in your .env file!

### Step 6: Start Services

```bash
# Start all services
docker-compose up -d

# Wait 15 seconds
sleep 15

# Check status
docker-compose ps
```

**Expected**: All services should be "Up"

### Step 7: Initialize Database

```bash
# Initialize database
docker-compose exec app python -m app.core.init_db
```

**Expected**: "Database initialization completed!"

### Step 8: Verify Application

```bash
# Check logs
docker-compose logs -f app

# Look for:
# - "Application started"
# - "Monitoring scheduler started"
# - No errors

# Press Ctrl+C to exit logs
```

**Test API**:
```bash
# From your server
curl http://localhost:8000/health

# Expected: {"status":"healthy","scheduler_running":true}
```

**Test from your local machine**:
```bash
# From your Mac (replace IP)
curl http://YOUR_SERVER_IP:8000/health
```

If this works, your application is running!

---

## Phase 4: Setup Domain & SSL (Optional - 30 minutes)

### If you have a domain:

**On your domain registrar** (Namecheap, GoDaddy, etc.):
1. Add A record: `@` → `YOUR_SERVER_IP`
2. Add A record: `www` → `YOUR_SERVER_IP`
3. Wait 5-10 minutes for DNS propagation

**On your server**:

```bash
# Install Nginx
apt install nginx -y

# Install Certbot (for SSL)
apt install certbot python3-certbot-nginx -y

# Create Nginx config
nano /etc/nginx/sites-available/termin-notify
```

**Add this configuration** (replace `termin-notify.de` with your domain):

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

**Enable and start Nginx**:
```bash
# Create symlink
ln -s /etc/nginx/sites-available/termin-notify /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Reload Nginx
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d termin-notify.de -d www.termin-notify.de
```

Follow prompts:
- Enter email
- Agree to terms
- Choose: Redirect HTTP to HTTPS

**Test**:
```bash
# From your Mac
curl https://termin-notify.de/health
```

### If you DON'T have a domain yet:

You can use the IP address for now:
- API: `http://YOUR_SERVER_IP:8000`
- Docs: `http://YOUR_SERVER_IP:8000/docs`

Buy domain later and add SSL then.

---

## Phase 5: Post-Deployment Validation (15 minutes)

### Test All Features

**From your production server** (http://YOUR_DOMAIN or http://YOUR_IP:8000/docs):

1. ✅ **Health check**:
   ```bash
   curl http://YOUR_DOMAIN/health
   # or
   curl http://YOUR_IP:8000/health
   ```

2. ✅ **Register user** (use API docs):
   - Open browser: http://YOUR_DOMAIN/docs (or http://YOUR_IP:8000/docs)
   - POST /api/auth/register
   - Register with your real email

3. ✅ **Check email** (welcome email should arrive)

4. ✅ **Login and get token**

5. ✅ **Create subscription**

6. ✅ **Check monitoring is running**:
   ```bash
   docker-compose logs -f app | grep "Monitoring cycle"
   # Should see "Starting monitoring cycle..." every 5 minutes
   ```

7. ✅ **Check database**:
   ```bash
   docker-compose exec app python manage.py stats
   ```

---

## Phase 6: Setup Automated Backups (10 minutes)

```bash
# Create backup directory
mkdir -p /opt/backups

# Create backup script
nano /opt/backup.sh
```

**Add this content**:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
cd /opt/termin-notify
docker-compose exec -T postgres pg_dump -U termin_user termin_notify | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
```

**Make executable and schedule**:
```bash
chmod +x /opt/backup.sh

# Add to cron (daily at 2 AM)
crontab -e
```

Add this line:
```
0 2 * * * /opt/backup.sh >> /var/log/backup.log 2>&1
```

Save and exit.

---

## ✅ Deployment Validation Checklist

- [ ] Server created on Hetzner
- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] Environment configured (.env file)
- [ ] Database password changed in docker-compose.yml
- [ ] Services started successfully
- [ ] Database initialized
- [ ] Health check responds
- [ ] User registration works
- [ ] Email notifications work
- [ ] Monitoring scheduler running
- [ ] Backups configured
- [ ] (Optional) Domain and SSL configured

---

## Phase 7: First Launch (After Validation)

Once everything is validated:

### 1. Create First Real User

Use YOUR email address:
- Register via API: http://YOUR_DOMAIN/docs
- Verify welcome email arrives
- Subscribe to Berlin Bürgeramt (or your city)

### 2. Monitor for 24 Hours

```bash
# Check logs periodically
ssh root@YOUR_SERVER_IP
cd /opt/termin-notify
docker-compose logs -f app

# Look for:
# - Scraping cycles running every 5 minutes
# - No errors
# - If appointments found, notifications sent
```

### 3. Invite Beta Testers

Invite 5-10 friends/colleagues:
- Share registration link
- Ask them to subscribe to services
- Collect feedback

### 4. Start Marketing (Week 2)

Once validated:
- Post on Reddit (use templates from MARKETING.md)
- Post in Facebook groups
- Email outreach to Bürgerämter

---

## Common Issues & Solutions

### Issue: "Cannot connect to Docker daemon"

**Solution**: Start Docker Desktop on your Mac

### Issue: "Port 8000 already in use"

**Solution**:
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

### Issue: "Database connection failed"

**Solution**:
```bash
# Check postgres is running
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres
```

### Issue: "Email not sending"

**Solution**:
- Verify SMTP credentials in .env
- Check Gmail app password is correct
- Check logs: `docker-compose logs app | grep -i email`

### Issue: "Scraper finding 0 appointments"

**This is normal!** Most government sites have no appointments available. The scraper is working correctly, it just means there are no appointments at the moment.

---

## Monitoring Commands

```bash
# View real-time logs
docker-compose logs -f app

# View last 100 lines
docker-compose logs --tail=100 app

# Check service status
docker-compose ps

# Restart application
docker-compose restart app

# Restart all services
docker-compose restart

# View resource usage
docker stats

# Database stats
docker-compose exec app python manage.py stats

# List users
docker-compose exec app python manage.py users

# List services
docker-compose exec app python manage.py services
```

---

## Next Steps After Successful Deployment

1. ✅ **Validation complete** → Application running in production
2. ⏳ **Add legal pages** (Impressum, Datenschutz, AGB)
3. ⏳ **Setup Stripe** (payments)
4. ⏳ **Soft launch** (Reddit, Facebook)
5. ⏳ **Collect feedback**
6. ⏳ **Iterate and improve**

---

## Support

If you encounter issues:

1. Check logs: `docker-compose logs -f app`
2. Verify services: `docker-compose ps`
3. Review this guide
4. Check DEPLOYMENT.md
5. Review error messages carefully

---

**You're ready to deploy! Follow this guide step by step and you'll have Termin-Notify live in production within 2-3 hours.**

Good luck! 🚀
