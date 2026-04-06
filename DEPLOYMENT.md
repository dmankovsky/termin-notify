# Deployment Guide - Termin-Notify

## Quick Deploy to Hetzner VPS

### 1. Create Hetzner Cloud Server

Go to https://console.hetzner.cloud/

**Recommended Server**:
- Type: CX21 (2 vCPU, 4GB RAM, 40GB SSD)
- Location: Nuremberg (Germany - for GDPR, low latency)
- Image: Ubuntu 22.04
- Price: ~€6/month

**Initial Setup**: €6-10/month (scales with usage)

### 2. Initial Server Setup

```bash
# SSH into server
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

# Create app user
useradd -m -s /bin/bash termin
usermod -aG docker termin
```

### 3. Clone and Configure

```bash
# Switch to app user
su - termin

# Clone repository
cd /home/termin
git clone YOUR_REPO_URL termin-notify
cd termin-notify

# Create production .env file
nano .env
```

**.env Configuration**:
```env
# Database
DATABASE_URL=postgresql+asyncpg://termin_user:STRONG_PASSWORD_HERE@postgres:5432/termin_notify
DATABASE_URL_SYNC=postgresql://termin_user:STRONG_PASSWORD_HERE@postgres:5432/termin_notify

# Redis
REDIS_URL=redis://redis:6379/0

# Application
SECRET_KEY=GENERATE_RANDOM_STRING_HERE
ENVIRONMENT=production
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000

# Email (Gmail App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=noreply@termin-notify.de

# Stripe (get from stripe.com)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Scraping
SCRAPE_INTERVAL_MINUTES=5
MAX_CONCURRENT_SCRAPES=3
```

**Generate SECRET_KEY**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Deploy Application

```bash
# Build and start services
docker-compose up -d

# Wait for services to start
sleep 10

# Initialize database
docker-compose exec app python -m app.core.init_db

# Check logs
docker-compose logs -f
```

### 5. Setup Domain & SSL (Optional but Recommended)

**Buy a domain** (e.g., namecheap.com, godaddy.com):
- Cost: ~€10/year
- Example: `termin-notify.de`

**Point domain to server**:
1. Go to your domain registrar
2. Add A record: `@` → `YOUR_SERVER_IP`
3. Add A record: `www` → `YOUR_SERVER_IP`
4. Wait 5-10 minutes for DNS propagation

**Install Nginx + SSL**:

```bash
# As root
exit  # Exit from termin user
apt install nginx certbot python3-certbot-nginx -y

# Create Nginx configuration
nano /etc/nginx/sites-available/termin-notify
```

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

```bash
# Enable site
ln -s /etc/nginx/sites-available/termin-notify /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate (free from Let's Encrypt)
certbot --nginx -d termin-notify.de -d www.termin-notify.de

# Auto-renewal is configured automatically
```

### 6. Setup Monitoring & Auto-restart

**Create systemd service** (auto-restart on failure):

```bash
nano /etc/systemd/system/termin-notify.service
```

```ini
[Unit]
Description=Termin-Notify
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/termin/termin-notify
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=termin

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable termin-notify
systemctl start termin-notify
```

**Setup log rotation**:

```bash
nano /etc/logrotate.d/termin-notify
```

```
/home/termin/termin-notify/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 termin termin
    sharedscripts
}
```

### 7. Email Setup (Gmail)

1. Go to Google Account: https://myaccount.google.com/
2. Security → 2-Step Verification (enable if not enabled)
3. Security → App passwords
4. Generate app password for "Mail"
5. Copy 16-character password to `.env` as `SMTP_PASSWORD`

**Alternative Email Providers**:
- **SendGrid**: 100 emails/day free, then €15/month for 40k emails
- **AWS SES**: €0.10 per 1000 emails
- **Mailgun**: 5000 emails/month free

### 8. Stripe Payment Setup

1. Create account: https://stripe.com
2. Get API keys: Dashboard → Developers → API keys
3. Add to `.env`:
   - `STRIPE_SECRET_KEY`: sk_live_...
   - `STRIPE_PUBLISHABLE_KEY`: pk_live_...
4. Create products:
   - BASIC: €5/month
   - PRO: €10/month

### 9. Firewall Configuration

```bash
# Install UFW
apt install ufw -y

# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable
```

### 10. Backup Strategy

**Database Backups**:

```bash
# Create backup script
nano /home/termin/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/termin/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U termin_user termin_notify | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
```

```bash
chmod +x /home/termin/backup.sh

# Add to cron (daily at 2 AM)
crontab -e
```

Add: `0 2 * * * /home/termin/backup.sh`

## Cost Breakdown

### Monthly Costs

| Item | Cost |
|------|------|
| Hetzner VPS CX21 | €6/month |
| Domain | €1/month (€10/year) |
| Email (SendGrid free tier) | €0 |
| SSL Certificate (Let's Encrypt) | €0 |
| **Total** | **€7/month** |

### Scaling Costs

As you grow:
- 100 users: CX21 (€6/month) ✅
- 1,000 users: CX31 (€12/month)
- 10,000 users: CX41 (€24/month) + managed DB

## Maintenance

### Update Application

```bash
cd /home/termin/termin-notify
git pull
docker-compose down
docker-compose up -d --build
```

### View Logs

```bash
# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f postgres

# All logs
docker-compose logs -f
```

### Monitor Performance

```bash
# Docker stats
docker stats

# Database connections
docker-compose exec postgres psql -U termin_user -d termin_notify -c "SELECT count(*) FROM pg_stat_activity;"

# Disk usage
df -h
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart app only
docker-compose restart app
```

## Troubleshooting

### Application won't start

```bash
# Check logs
docker-compose logs app

# Check database connection
docker-compose exec app python -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### Email not sending

1. Check SMTP credentials in `.env`
2. Check Gmail app password is correct
3. Check logs: `docker-compose logs app | grep email`

### Database connection errors

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

## Security Best Practices

1. ✅ Use strong passwords for database
2. ✅ Keep SECRET_KEY secret and random
3. ✅ Enable firewall (UFW)
4. ✅ Use SSL certificate
5. ✅ Regular backups
6. ✅ Update system regularly: `apt update && apt upgrade`
7. ✅ Don't expose PostgreSQL port (keep in Docker network)
8. ✅ Use environment variables, never hardcode secrets

## Legal Requirements (Germany)

### Impressum (Required)

Add to your website:
```
Angaben gemäß § 5 TMG:
[Your Name]
[Your Address]
[Your Email]

Umsatzsteuer-ID: [Your Tax ID if >€22k revenue]
```

### Datenschutzerklärung (GDPR)

Use generator: https://www.datenschutz-generator.de/

### AGB (Terms of Service)

Include:
- Service description
- Pricing and payment terms
- Cancellation policy
- Liability limitations

### Tax Registration

1. Register Gewerbe (you already have this ✅)
2. Report to Finanzamt
3. If revenue > €22,000/year: charge Umsatzsteuer (19%)
4. Keep invoices and receipts for 10 years

## Go Live Checklist

- [ ] Domain purchased and configured
- [ ] SSL certificate installed
- [ ] Email sending working
- [ ] Database backups configured
- [ ] Firewall enabled
- [ ] Monitoring setup
- [ ] Stripe configured (for payments)
- [ ] Legal pages added (Impressum, Datenschutz, AGB)
- [ ] Test user registration
- [ ] Test notification flow
- [ ] Test payment flow

## Support

For deployment issues, check:
1. Application logs: `docker-compose logs -f`
2. Server resources: `htop` or `docker stats`
3. Disk space: `df -h`

Good luck! 🚀
