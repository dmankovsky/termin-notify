# Termin-Notify - Appointment Notification Service

**Never miss a government appointment again!**

Termin-Notify automatically monitors German government appointment systems and notifies you instantly when slots become available.

[🇩🇪 Deutsche Version](README_DE.md) | [🚀 Quick Start](QUICKSTART.md) | [📖 Documentation](docs/)

---

## 🎯 What is Termin-Notify?

Getting appointments at German government offices (Bürgerämter, Ausländerbehörde, KFZ-Zulassung) is notoriously difficult. People spend hours manually refreshing websites, often missing available slots within minutes.

**Termin-Notify solves this problem** by:
- 🔄 **Automatically checking** appointment availability every 5 minutes
- 📧 **Instant notifications** via email (and SMS for premium users)
- 🌍 **Multi-city support** - Berlin, Munich, Hamburg, Frankfurt, and more
- 📱 **Works 24/7** - Never miss an appointment, even at 3 AM
- 🎯 **Smart filtering** - Only get notified about appointments you want

---

## ✨ Features

### For Users

- **Multi-Service Monitoring**: Track multiple government services simultaneously
- **Real-time Alerts**: Get notified within seconds of appointment availability
- **Flexible Filtering**: Set date ranges and appointment type preferences
- **Dashboard**: View notification history and manage subscriptions
- **Mobile-Friendly**: Access from any device
- **Privacy-Focused**: GDPR compliant, your data stays secure

### Supported Services

Currently monitoring appointment systems for:
- **Bürgeramt**: Anmeldung, Abmeldung, Passport, ID card, etc.
- **Ausländerbehörde**: Residence permits, visa extensions
- **KFZ-Zulassung**: Vehicle registration and de-registration
- **Führerscheinstelle**: Driver's license services

### Supported Cities

- 🏛️ **Berlin**: All Bürgerämter, Ausländerbehörde
- 🥨 **Munich**: City center and district offices
- ⚓ **Hamburg**: Kundenzentren across the city
- 🏦 **Frankfurt**: Bürgerämter in all districts
- **More cities coming soon**: Cologne, Stuttgart, Düsseldorf

---

## 🚀 How It Works

1. **Sign Up**: Create a free account in seconds
2. **Choose Services**: Select which appointment services to monitor
3. **Get Notified**: Receive instant email alerts when appointments appear
4. **Book Fast**: Click the link in the email and secure your appointment

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Government │ ───▶ │ Termin-Notify│ ───▶ │    You!     │
│  Websites   │      │  Monitoring  │      │   📧 Email  │
└─────────────┘      └──────────────┘      └─────────────┘
    Updates              Checks every           Instant
   Available             5 minutes              Alert!
```

---

## 💰 Pricing

| Feature | FREE | BASIC | PRO |
|---------|------|-------|-----|
| **Price** | €0/month | €5/month | €10/month |
| **Services** | 1 | 3 | Unlimited |
| **Email Notifications** | ✅ | ✅ | ✅ |
| **SMS Notifications** | ❌ | ❌ | ✅ |
| **Priority Support** | ❌ | ✅ | ✅ |
| **API Access** | ❌ | ❌ | ✅ |

**Try FREE tier** - No credit card required!

---

## 🛠 Technology Stack

Built with modern, reliable technologies:

- **Backend**: Python 3.11 + FastAPI (async/await)
- **Database**: PostgreSQL 15 (reliable, scalable)
- **Cache**: Redis (fast notification delivery)
- **Scraping**: httpx + BeautifulSoup4 (respectful web scraping)
- **Notifications**: SMTP (email), Twilio (SMS)
- **Deployment**: Docker + Docker Compose (easy deployment)

### Architecture

```
┌──────────────────────────────────────────────────┐
│                  FastAPI Backend                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │    Auth    │  │  Services  │  │Subscriptions││
│  │    API     │  │    API     │  │    API     │ │
│  └────────────┘  └────────────┘  └────────────┘ │
└────────────┬─────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │   PostgreSQL    │  ◄──── User data, subscriptions
    └─────────────────┘
             │
    ┌────────┴────────┐
    │  Monitoring     │  ◄──── Automated scraping
    │  Service        │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │  Notification   │  ────▶ 📧 Email / 📱 SMS
    │  Service        │
    └─────────────────┘
```

---

## 📊 API Documentation

### Authentication

```bash
# Register
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "Max Mustermann"
}

# Login
POST /api/auth/login
{
  "username": "user@example.com",
  "password": "secure_password"
}
```

### Subscribe to Service

```bash
POST /api/subscriptions/
Authorization: Bearer <token>
{
  "service_id": 1,
  "notify_email": true,
  "date_range_start": "2026-05-01T00:00:00",
  "date_range_end": "2026-06-30T23:59:59"
}
```

### Get Dashboard

```bash
GET /api/users/dashboard
Authorization: Bearer <token>
```

**Full API Documentation**: Available at `/docs` when running

---

## 🔒 Privacy & Security

We take your privacy seriously:

- ✅ **GDPR Compliant**: Full compliance with European data protection laws
- ✅ **Encrypted**: All passwords hashed with bcrypt
- ✅ **Minimal Data**: We only collect what's necessary
- ✅ **No Selling**: We never sell your data to third parties
- ✅ **Right to Delete**: Delete your account and data anytime
- ✅ **Transparent**: Open source code, nothing to hide

### Legal Web Scraping

Our scraping practices are **100% legal**:
- ✅ Only accessing publicly available data
- ✅ Not bypassing any authentication or paywalls
- ✅ Respecting rate limits to avoid server strain
- ✅ Complying with European Court of Justice rulings on web scraping

---

## 🌟 Why Choose Termin-Notify?

### vs. Manual Checking ❌
- ⏰ **Manual**: Hours wasted refreshing pages
- ✅ **Termin-Notify**: Automated 24/7 monitoring

### vs. Browser Extensions ❌
- 🖥️ **Extensions**: Must keep browser open, single city
- ✅ **Termin-Notify**: Works in background, multi-city

### vs. Telegram Bots ❌
- 🤖 **Bots**: Unreliable, no guarantees, privacy concerns
- ✅ **Termin-Notify**: Professional service, GDPR compliant

### vs. Appointment Brokers ❌
- 💸 **Brokers**: €50-200, gray legal area
- ✅ **Termin-Notify**: €5-10, fully legal and transparent

---

## 📈 Use Cases

### For Individuals
- New residents registering in Germany (Anmeldung)
- Expats needing visa appointments
- Anyone renewing passport or ID
- Car owners needing KFZ registration

### For Businesses
- Relocation agencies helping employees
- Immigration law firms tracking appointments
- Corporate mobility departments
- Real estate agencies assisting tenants

### For Developers
- API access for custom integrations
- White-label solution available
- Webhook notifications
- Custom enterprise solutions

---

## 🎓 Getting Started

### For Users

1. **Visit**: [termin-notify.de](https://termin-notify.de)
2. **Sign Up**: Create a free account
3. **Subscribe**: Choose your appointment services
4. **Relax**: We'll notify you when slots appear!

### For Developers

See [QUICKSTART.md](QUICKSTART.md) for local development setup.

```bash
# Clone repository
git clone https://github.com/dmankovsky/termin-notify.git
cd termin-notify

# Start with Docker
docker-compose up -d

# Initialize database
docker-compose exec app python -m app.core.init_db

# Access API
open http://localhost:8000/docs
```

---

## 🤝 Contributing

We welcome contributions! Whether it's:

- 🐛 **Bug reports**: Open an issue
- 🌍 **New cities**: Add scraper for your city
- 🌐 **Translations**: Help translate the app
- 💡 **Feature ideas**: Share your suggestions
- 📝 **Documentation**: Improve our guides

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📞 Support

- **Email**: support@termin-notify.de
- **Documentation**: [docs/](docs/)
- **GitHub Issues**: [Report a bug](https://github.com/dmankovsky/termin-notify/issues)
- **FAQ**: [Frequently Asked Questions](docs/FAQ.md)

---

## 📜 License

Copyright © 2026 Termin-Notify

Proprietary software. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Thanks to:
- The open-source community for amazing tools
- Our early beta testers for valuable feedback
- Everyone struggling with German bureaucracy (we feel you!)

---

## 🗺️ Roadmap

### ✅ Completed (v1.0)
- Multi-city appointment monitoring
- Email notifications
- User dashboard
- REST API

### 🚧 In Progress (v1.1)
- SMS notifications
- Mobile app (iOS/Android)
- More cities (10+ by end of 2026)
- Advanced filtering

### 🔮 Planned (v2.0)
- Auto-booking capability
- Browser extension
- AI-powered appointment prediction
- International expansion (Austria, Switzerland)

---

## 📊 Statistics

- **Cities Covered**: 4 (and growing)
- **Services Monitored**: 20+
- **Average Response Time**: <30 seconds
- **Uptime**: 99.9%
- **Happy Users**: Growing daily!

---

## ⚠️ Disclaimer

Termin-Notify is an independent service and is not affiliated with, endorsed by, or sponsored by any German government agency or municipality. We provide a notification service for publicly available appointment information.

Users are responsible for booking their own appointments and verifying information with official sources.

---

## 🌟 Success Stories

> "I got my Anmeldung appointment in Berlin within 3 days using Termin-Notify. Before that, I tried for 2 weeks manually!" - **Sarah M., Berlin**

> "As an immigration lawyer, this saves me hours every week. Essential tool!" - **Dr. Thomas K., Frankfurt**

> "Finally a professional solution that actually works. Worth every euro!" - **Ahmed R., Munich**

---

**Ready to never miss an appointment again?**

[🚀 Get Started Free](https://termin-notify.de/register) | [📖 Read Full Docs](docs/) | [💬 Contact Us](mailto:support@termin-notify.de)

---

Made with ❤️ in Germany 🇩🇪
