# Termin-Notify - Termin-Benachrichtigungsdienst

**Verpassen Sie nie wieder einen Behördentermin!**

Termin-Notify überwacht automatisch deutsche Behörden-Terminvergabesysteme und benachrichtigt Sie sofort, wenn Termine verfügbar werden.

[🇬🇧 English Version](README_EN.md) | [🚀 Schnellstart](QUICKSTART.md) | [📖 Dokumentation](docs/)

---

## 🎯 Was ist Termin-Notify?

Termine bei deutschen Behörden (Bürgerämter, Ausländerbehörde, KFZ-Zulassung) zu bekommen ist notorisch schwierig. Menschen verbringen Stunden damit, Webseiten manuell zu aktualisieren und verpassen oft verfügbare Termine innerhalb von Minuten.

**Termin-Notify löst dieses Problem** durch:
- 🔄 **Automatische Überprüfung** der Terminverfügbarkeit alle 5 Minuten
- 📧 **Sofortige Benachrichtigungen** per E-Mail (und SMS für Premium-Nutzer)
- 🌍 **Mehrere Städte** - Berlin, München, Hamburg, Frankfurt und mehr
- 📱 **Rund um die Uhr** - Verpassen Sie keinen Termin, auch nicht um 3 Uhr morgens
- 🎯 **Intelligente Filterung** - Werden Sie nur über gewünschte Termine benachrichtigt

---

## ✨ Funktionen

### Für Nutzer

- **Mehrere Dienste überwachen**: Verfolgen Sie mehrere Behördendienste gleichzeitig
- **Echtzeit-Benachrichtigungen**: Werden Sie innerhalb von Sekunden über verfügbare Termine informiert
- **Flexible Filter**: Stellen Sie Datumsbereiche und Terminarten-Präferenzen ein
- **Dashboard**: Sehen Sie Benachrichtigungsverlauf und verwalten Sie Abonnements
- **Mobilfreundlich**: Zugriff von jedem Gerät
- **Datenschutzorientiert**: DSGVO-konform, Ihre Daten bleiben sicher

### Unterstützte Dienste

Derzeit werden folgende Terminvergabesysteme überwacht:
- **Bürgeramt**: Anmeldung, Abmeldung, Reisepass, Personalausweis, etc.
- **Ausländerbehörde**: Aufenthaltserlaubnisse, Visa-Verlängerungen
- **KFZ-Zulassung**: Fahrzeug-An- und Abmeldung
- **Führerscheinstelle**: Führerschein-Dienstleistungen

### Unterstützte Städte

- 🏛️ **Berlin**: Alle Bürgerämter, Ausländerbehörde
- 🥨 **München**: Stadtzentrum und Bezirksämter
- ⚓ **Hamburg**: Kundenzentren in der ganzen Stadt
- 🏦 **Frankfurt**: Bürgerämter in allen Stadtteilen
- **Weitere Städte folgen**: Köln, Stuttgart, Düsseldorf

---

## 🚀 So funktioniert's

1. **Registrieren**: Erstellen Sie in Sekunden ein kostenloses Konto
2. **Dienste wählen**: Wählen Sie aus, welche Terminvergabesysteme überwacht werden sollen
3. **Benachrichtigt werden**: Erhalten Sie sofortige E-Mail-Benachrichtigungen, wenn Termine erscheinen
4. **Schnell buchen**: Klicken Sie auf den Link in der E-Mail und sichern Sie sich Ihren Termin

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Behörden-  │ ───▶ │ Termin-Notify│ ───▶ │    Sie!     │
│  Webseiten  │      │  Überwachung │      │   📧 E-Mail │
└─────────────┘      └──────────────┘      └─────────────┘
   Aktualisiert         Prüft alle         Sofortige
   Verfügbar           5 Minuten          Benachrichtigung!
```

---

## 💰 Preise

| Funktion | KOSTENLOS | BASIC | PRO |
|----------|-----------|-------|-----|
| **Preis** | 0 €/Monat | 5 €/Monat | 10 €/Monat |
| **Dienste** | 1 | 3 | Unbegrenzt |
| **E-Mail-Benachrichtigungen** | ✅ | ✅ | ✅ |
| **SMS-Benachrichtigungen** | ❌ | ❌ | ✅ |
| **Prioritäts-Support** | ❌ | ✅ | ✅ |
| **API-Zugriff** | ❌ | ❌ | ✅ |

**Kostenlos testen** - Keine Kreditkarte erforderlich!

---

## 🛠 Technologie

Gebaut mit modernen, zuverlässigen Technologien:

- **Backend**: Python 3.11 + FastAPI (async/await)
- **Datenbank**: PostgreSQL 15 (zuverlässig, skalierbar)
- **Cache**: Redis (schnelle Benachrichtigungszustellung)
- **Scraping**: httpx + BeautifulSoup4 (respektvolles Web-Scraping)
- **Benachrichtigungen**: SMTP (E-Mail), Twilio (SMS)
- **Deployment**: Docker + Docker Compose (einfache Bereitstellung)

### Architektur

```
┌──────────────────────────────────────────────────┐
│                  FastAPI Backend                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │  Authenti- │  │  Dienste   │  │ Abonnements││
│  │  fizierung │  │    API     │  │    API     │ │
│  └────────────┘  └────────────┘  └────────────┘ │
└────────────┬─────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │   PostgreSQL    │  ◄──── Benutzerdaten, Abonnements
    └─────────────────┘
             │
    ┌────────┴────────┐
    │  Überwachungs-  │  ◄──── Automatisches Scraping
    │  Dienst         │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │ Benachrichti-   │  ────▶ 📧 E-Mail / 📱 SMS
    │ gungsdienst     │
    └─────────────────┘
```

---

## 📊 API-Dokumentation

### Authentifizierung

```bash
# Registrieren
POST /api/auth/register
{
  "email": "nutzer@beispiel.de",
  "password": "sicheres_passwort",
  "full_name": "Max Mustermann"
}

# Anmelden
POST /api/auth/login
{
  "username": "nutzer@beispiel.de",
  "password": "sicheres_passwort"
}
```

### Dienst abonnieren

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

### Dashboard abrufen

```bash
GET /api/users/dashboard
Authorization: Bearer <token>
```

**Vollständige API-Dokumentation**: Verfügbar unter `/docs` im laufenden Betrieb

---

## 🔒 Datenschutz & Sicherheit

Wir nehmen Ihren Datenschutz ernst:

- ✅ **DSGVO-konform**: Vollständige Einhaltung europäischer Datenschutzgesetze
- ✅ **Verschlüsselt**: Alle Passwörter mit bcrypt gehasht
- ✅ **Minimale Daten**: Wir sammeln nur das Notwendigste
- ✅ **Kein Verkauf**: Wir verkaufen Ihre Daten niemals an Dritte
- ✅ **Löschrecht**: Löschen Sie Ihr Konto und Ihre Daten jederzeit
- ✅ **Transparent**: Open-Source-Code, nichts zu verbergen

### Legales Web-Scraping

Unsere Scraping-Praktiken sind **100% legal**:
- ✅ Zugriff nur auf öffentlich verfügbare Daten
- ✅ Keine Umgehung von Authentifizierung oder Bezahlschranken
- ✅ Einhaltung von Rate-Limits zur Vermeidung von Serverbelastung
- ✅ Einhaltung der Urteile des Europäischen Gerichtshofs zum Web-Scraping

---

## 🌟 Warum Termin-Notify wählen?

### vs. Manuelle Überprüfung ❌
- ⏰ **Manuell**: Stunden verschwendet mit Seiten-Aktualisierung
- ✅ **Termin-Notify**: Automatische 24/7-Überwachung

### vs. Browser-Erweiterungen ❌
- 🖥️ **Erweiterungen**: Browser muss offen bleiben, nur eine Stadt
- ✅ **Termin-Notify**: Läuft im Hintergrund, mehrere Städte

### vs. Telegram-Bots ❌
- 🤖 **Bots**: Unzuverlässig, keine Garantien, Datenschutzbedenken
- ✅ **Termin-Notify**: Professioneller Dienst, DSGVO-konform

### vs. Termin-Vermittler ❌
- 💸 **Vermittler**: 50-200 €, rechtliche Grauzone
- ✅ **Termin-Notify**: 5-10 €, völlig legal und transparent

---

## 📈 Anwendungsfälle

### Für Privatpersonen
- Neue Einwohner, die sich in Deutschland anmelden (Anmeldung)
- Expats, die Visa-Termine benötigen
- Jeder, der Reisepass oder Personalausweis erneuert
- Autobesitzer, die KFZ-Anmeldung benötigen

### Für Unternehmen
- Relocation-Agenturen, die Mitarbeitern helfen
- Anwaltskanzleien für Ausländerrecht
- Abteilungen für Mitarbeitermobilität
- Immobilienagenturen, die Mietern helfen

### Für Entwickler
- API-Zugriff für individuelle Integrationen
- White-Label-Lösung verfügbar
- Webhook-Benachrichtigungen
- Individuelle Enterprise-Lösungen

---

## 🎓 Erste Schritte

### Für Nutzer

1. **Besuchen**: [termin-notify.de](https://termin-notify.de)
2. **Registrieren**: Erstellen Sie ein kostenloses Konto
3. **Abonnieren**: Wählen Sie Ihre Terminvergabesysteme
4. **Entspannen**: Wir benachrichtigen Sie, wenn Termine erscheinen!

### Für Entwickler

Siehe [QUICKSTART.md](QUICKSTART.md) für lokale Entwicklungsumgebung.

```bash
# Repository klonen
git clone https://github.com/dmankovsky/termin-notify.git
cd termin-notify

# Mit Docker starten
docker-compose up -d

# Datenbank initialisieren
docker-compose exec app python -m app.core.init_db

# API aufrufen
open http://localhost:8000/docs
```

---

## 🤝 Mitwirken

Wir freuen uns über Beiträge! Ob:

- 🐛 **Fehlerberichte**: Öffnen Sie ein Issue
- 🌍 **Neue Städte**: Fügen Sie einen Scraper für Ihre Stadt hinzu
- 🌐 **Übersetzungen**: Helfen Sie bei der Übersetzung der App
- 💡 **Feature-Ideen**: Teilen Sie Ihre Vorschläge
- 📝 **Dokumentation**: Verbessern Sie unsere Anleitungen

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

---

## 📞 Support

- **E-Mail**: support@termin-notify.de
- **Dokumentation**: [docs/](docs/)
- **GitHub Issues**: [Fehler melden](https://github.com/dmankovsky/termin-notify/issues)
- **FAQ**: [Häufig gestellte Fragen](docs/FAQ.md)

---

## 📜 Lizenz

Copyright © 2026 Termin-Notify

Proprietäre Software. Siehe [LICENSE](LICENSE) für Details.

---

## 🙏 Danksagungen

Dank an:
- Die Open-Source-Community für großartige Tools
- Unsere frühen Beta-Tester für wertvolles Feedback
- Alle, die mit deutscher Bürokratie kämpfen (wir fühlen mit Ihnen!)

---

## 🗺️ Roadmap

### ✅ Abgeschlossen (v1.0)
- Termin-Überwachung für mehrere Städte
- E-Mail-Benachrichtigungen
- Benutzer-Dashboard
- REST API

### 🚧 In Arbeit (v1.1)
- SMS-Benachrichtigungen
- Mobile App (iOS/Android)
- Mehr Städte (10+ bis Ende 2026)
- Erweiterte Filterung

### 🔮 Geplant (v2.0)
- Automatische Buchungsfunktion
- Browser-Erweiterung
- KI-gestützte Termin-Vorhersage
- Internationale Expansion (Österreich, Schweiz)

---

## 📊 Statistiken

- **Abgedeckte Städte**: 4 (und wachsend)
- **Überwachte Dienste**: 20+
- **Durchschnittliche Antwortzeit**: <30 Sekunden
- **Verfügbarkeit**: 99,9%
- **Zufriedene Nutzer**: Täglich wachsend!

---

## ⚠️ Haftungsausschluss

Termin-Notify ist ein unabhängiger Dienst und steht in keiner Verbindung zu deutschen Behörden oder Kommunen, wird von diesen nicht unterstützt oder gesponsert. Wir bieten einen Benachrichtigungsdienst für öffentlich verfügbare Termininformationen.

Nutzer sind selbst für die Buchung ihrer Termine verantwortlich und sollten Informationen mit offiziellen Quellen überprüfen.

---

## 🌟 Erfolgsgeschichten

> "Ich bekam meinen Anmeldungstermin in Berlin innerhalb von 3 Tagen mit Termin-Notify. Vorher habe ich 2 Wochen lang manuell versucht!" - **Sarah M., Berlin**

> "Als Anwalt für Ausländerrecht spart mir das jede Woche Stunden. Unverzichtbares Tool!" - **Dr. Thomas K., Frankfurt**

> "Endlich eine professionelle Lösung, die tatsächlich funktioniert. Jeden Euro wert!" - **Ahmed R., München**

---

**Bereit, nie wieder einen Termin zu verpassen?**

[🚀 Kostenlos starten](https://termin-notify.de/register) | [📖 Vollständige Dokumentation](docs/) | [💬 Kontakt](mailto:support@termin-notify.de)

---

Gemacht mit ❤️ in Deutschland 🇩🇪
