# Termin-Notify

**Automated Appointment Notification Service for German Government Offices**

Never miss a Bürgeramt, Ausländerbehörde, or KFZ-Zulassung appointment again!

---

## 📖 Documentation

**Choose your language / Wählen Sie Ihre Sprache:**

- 🇬🇧 [**English Documentation**](README_EN.md)
- 🇩🇪 [**Deutsche Dokumentation**](README_DE.md)

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/dmankovsky/termin-notify.git
cd termin-notify

# Start with Docker
docker-compose up -d

# Initialize database
docker-compose exec app python -m app.core.init_db

# Access API docs
open http://localhost:8000/docs
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

---

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **[Deployment Guide](DEPLOYMENT.md)** - Deploy to production (Hetzner VPS)
- **[Business Plan](BUSINESS_PLAN.md)** - Market analysis & revenue strategy
- **[Marketing Strategy](MARKETING.md)** - Email templates & outreach plan
- **[Project Summary](PROJECT_SUMMARY.md)** - Complete overview

---

## ✨ Features

- 🔄 **Automated Monitoring** - Checks every 5 minutes
- 📧 **Instant Notifications** - Email + SMS alerts
- 🌍 **Multi-City Support** - Berlin, Munich, Hamburg, Frankfurt
- 📱 **API Access** - RESTful API for integrations
- 🔒 **GDPR Compliant** - Privacy-focused & secure
- 🎯 **Smart Filtering** - Date ranges & appointment types

---

## 💰 Pricing

| Tier | Price | Services | Notifications |
|------|-------|----------|---------------|
| **FREE** | €0/mo | 1 | Email |
| **BASIC** | €5/mo | 3 | Email |
| **PRO** | €10/mo | ∞ | Email + SMS |

---

## 🛠 Technology

- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Deployment**: Docker + Docker Compose
- **Monitoring**: APScheduler
- **Notifications**: SMTP + Twilio

---

## 📊 Project Status

✅ **MVP Complete** - Production ready
- [x] Multi-city scraping (4 cities)
- [x] Email notifications
- [x] User authentication & management
- [x] Subscription system
- [x] RESTful API
- [x] Docker deployment
- [x] Comprehensive documentation

🚧 **Coming Soon**
- [ ] SMS notifications
- [ ] Mobile app (iOS/Android)
- [ ] Auto-booking feature
- [ ] 10+ cities

---

## 🎯 Use Cases

### For Individuals
- Anmeldung / Abmeldung
- Passport / ID renewal
- Visa appointments
- Vehicle registration

### For Businesses
- Relocation agencies
- Immigration law firms
- HR departments
- Real estate agencies

---

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📞 Support

- **Email**: support@termin-notify.de
- **Issues**: [GitHub Issues](https://github.com/dmankovsky/termin-notify/issues)
- **Documentation**: See [docs/](docs/)

---

## 📜 License

Copyright © 2026 Termin-Notify. All rights reserved.

See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built to solve real problems for real people struggling with German bureaucracy.

Made with ❤️ in Germany 🇩🇪

---

**Ready to get started?**

👉 [Read Full Documentation (English)](README_EN.md)
👉 [Vollständige Dokumentation lesen (Deutsch)](README_DE.md)
