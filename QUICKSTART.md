# Termin-Notify - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Docker & Docker Compose installed
- [ ] Gmail account (for sending emails)
- [ ] 15 minutes of your time

---

## Option 1: Docker (Fastest) ⚡

### 1. Clone & Configure

```bash
cd /Users/dmankovskyi/GitHub/Private/termin-notify

# Copy environment template
cp .env.example .env

# Edit .env and add your Gmail credentials
nano .env
```

**Required Settings in .env**:
```env
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=your-gmail@gmail.com
```

**Get Gmail App Password**:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already)
3. Search "App passwords"
4. Generate password for "Mail"
5. Copy 16-character password to `.env`

### 2. Start Services

```bash
# Start everything
docker-compose up -d

# Wait 10 seconds for database to start
sleep 10

# Initialize database with appointment services
docker-compose exec app python -m app.core.init_db

# Check if everything is running
docker-compose ps
```

### 3. Test the Application

```bash
# Create test user and run test scraper
docker-compose exec app python test_setup.py
```

### 4. Access the API

Open browser: http://localhost:8000/docs

You'll see the interactive API documentation (Swagger UI).

**Test Login**:
- Email: `test@example.com`
- Password: `testpassword123`

---

## Option 2: Local Development

### 1. Setup Python Environment

```bash
cd /Users/dmankovskyi/GitHub/Private/termin-notify

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start PostgreSQL & Redis

**Using Docker**:
```bash
# PostgreSQL
docker run -d \
  --name termin-postgres \
  -e POSTGRES_USER=termin_user \
  -e POSTGRES_PASSWORD=termin_password \
  -e POSTGRES_DB=termin_notify \
  -p 5432:5432 \
  postgres:15-alpine

# Redis
docker run -d \
  --name termin-redis \
  -p 6379:6379 \
  redis:7-alpine
```

**Using Homebrew (macOS)**:
```bash
brew install postgresql@15 redis
brew services start postgresql@15
brew services start redis

# Create database
createdb termin_notify
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env
```

Update database URLs:
```env
DATABASE_URL=postgresql+asyncpg://termin_user:termin_password@localhost:5432/termin_notify
DATABASE_URL_SYNC=postgresql://termin_user:termin_password@localhost:5432/termin_notify
```

### 4. Initialize & Run

```bash
# Initialize database
python -m app.core.init_db

# Run test setup
python test_setup.py

# Start application
uvicorn app.main:app --reload
```

---

## Common Commands

### View All Services

```bash
python manage.py services
```

### View All Users

```bash
python manage.py users
```

### Check Statistics

```bash
python manage.py stats
```

### View Logs

```bash
# Docker
docker-compose logs -f app

# Local
# Logs appear in terminal where uvicorn is running
```

### Restart Application

```bash
# Docker
docker-compose restart app

# Local
# Just Ctrl+C and re-run uvicorn command
```

---

## Test the Full Flow

### 1. Register a User (via API)

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "myemail@example.com",
    "password": "mypassword123",
    "full_name": "My Name"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=myemail@example.com&password=mypassword123"
```

Copy the `access_token` from response.

### 3. List Available Services

```bash
curl "http://localhost:8000/api/services/"
```

### 4. Subscribe to a Service

```bash
curl -X POST "http://localhost:8000/api/subscriptions/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": 1,
    "notify_email": true
  }'
```

### 5. Check Dashboard

```bash
curl "http://localhost:8000/api/users/dashboard" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## How It Works

1. **Scraper runs every 5 minutes** (configurable)
2. **Checks all active appointment services** for available slots
3. **When appointment found**:
   - Saves to database
   - Sends email to all subscribed users
   - Respects notification cooldown (15 min default)
4. **User receives email** with appointment details and booking link

---

## Troubleshooting

### "Connection refused" errors

**Problem**: PostgreSQL/Redis not running

**Solution**:
```bash
# Docker
docker-compose up -d postgres redis

# Local
brew services start postgresql@15 redis
```

### Email not sending

**Problem**: Wrong SMTP credentials

**Solution**:
1. Check `.env` has correct Gmail credentials
2. Make sure you used App Password, not regular password
3. Check logs: `docker-compose logs app | grep -i smtp`

### Scraper finding 0 appointments

**Expected behavior**: Most government sites have no available appointments.

**To verify scraper works**:
- Check logs for "Found X appointments"
- The scraper still runs successfully even when finding 0 slots
- Real appointments will trigger notifications when they appear

### Database errors

**Problem**: Database not initialized

**Solution**:
```bash
# Docker
docker-compose exec app python -m app.core.init_db

# Local
python -m app.core.init_db
```

---

## Next Steps

Now that you have it running:

1. **Test with real email** - Register with your own email and check inbox
2. **Customize scraping interval** - Edit `SCRAPE_INTERVAL_MINUTES` in `.env`
3. **Add more cities** - Create new scrapers (see README.md)
4. **Deploy to production** - See DEPLOYMENT.md
5. **Setup payments** - Integrate Stripe (see BUSINESS_PLAN.md)
6. **Start marketing** - Get your first users!

---

## Quick Reference

| Task | Command |
|------|---------|
| Start all services | `docker-compose up -d` |
| Stop all services | `docker-compose down` |
| View logs | `docker-compose logs -f app` |
| Restart app | `docker-compose restart app` |
| Run tests | `docker-compose exec app python test_setup.py` |
| Database shell | `docker-compose exec postgres psql -U termin_user -d termin_notify` |
| Python shell | `docker-compose exec app python` |
| List users | `python manage.py users` |
| List services | `python manage.py services` |
| Reset database | `python manage.py reset` |

---

## Support

- **Documentation**: See README.md
- **Business Plan**: See BUSINESS_PLAN.md
- **Deployment**: See DEPLOYMENT.md
- **Logs**: `docker-compose logs -f`

**The application is production-ready!** Just deploy to Hetzner VPS and start getting users.

Good luck! 🚀
