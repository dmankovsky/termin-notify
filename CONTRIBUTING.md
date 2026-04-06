# Contributing to Termin-Notify

Thank you for your interest in contributing to Termin-Notify!

## Ways to Contribute

### 1. Report Bugs 🐛

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### 2. Suggest Features 💡

Have an idea? Open an issue with:
- Description of the feature
- Use case / problem it solves
- Proposed implementation (optional)

### 3. Add New Cities 🌍

Help expand coverage to more German cities!

**Steps:**
1. Fork the repository
2. Create a new scraper in `app/scrapers/your_city.py`
3. Follow the `BaseScraper` interface
4. Test your scraper thoroughly
5. Submit a pull request

**Scraper Template:**

```python
from app.scrapers.base import BaseScraper, AppointmentSlot
from typing import List

class YourCityScraper(BaseScraper):
    async def scrape(self, url: str) -> List[AppointmentSlot]:
        # Your implementation
        pass
```

### 4. Improve Documentation 📝

- Fix typos
- Add examples
- Translate to other languages
- Write tutorials

### 5. Code Contributions 💻

**Before submitting:**
- Follow existing code style
- Add tests for new features
- Update documentation
- Ensure all tests pass

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/termin-notify.git
cd termin-notify

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start development server
uvicorn app.main:app --reload
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Keep functions focused and small

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### PR Guidelines

- Provide clear description of changes
- Link related issues
- Add screenshots for UI changes
- Ensure tests pass
- Update documentation

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_scrapers.py

# Run with coverage
pytest --cov=app tests/
```

## City Scraper Guidelines

When adding a new city scraper:

1. **Research** the appointment system
2. **Identify** HTML elements for dates/slots
3. **Handle** various response formats
4. **Add error handling** for edge cases
5. **Test** with real URLs
6. **Document** any quirks or limitations

### Example Scraper

```python
from app.scrapers.base import BaseScraper, AppointmentSlot
from datetime import datetime
import re

class StuttgartScraper(BaseScraper):
    """Scraper for Stuttgart Bürgeramt"""

    async def scrape(self, url: str) -> List[AppointmentSlot]:
        appointments = []

        # Fetch page
        html = await self.fetch_page(url)
        if not html:
            return appointments

        soup = self.parse_html(html)

        # Find appointment elements
        slots = soup.find_all('div', class_='appointment-slot')

        for slot in slots:
            try:
                date_str = slot.find('span', class_='date').text
                date = datetime.strptime(date_str, '%d.%m.%Y')

                appointment = AppointmentSlot(
                    date=date,
                    appointment_type='Bürgeramt Stuttgart',
                    location='Stuttgart',
                    booking_url=self.extract_booking_url(slot)
                )
                appointments.append(appointment)
            except Exception as e:
                logger.error(f"Error parsing slot: {e}")
                continue

        return appointments
```

## Adding Services to Database

After creating a scraper, add services to the database:

```python
# In app/core/init_db.py

{
    "name": "Bürgeramt Stuttgart Mitte",
    "service_type": ServiceType.BUERGERAMT,
    "city": City.STUTTGART,
    "url": "https://www.stuttgart.de/termine",
    "scraper_type": "stuttgart_buergeramt",
}
```

## Translation Guidelines

For German translations:
- Use formal "Sie" form
- Be clear and professional
- Maintain technical accuracy
- Follow German grammar rules

## Community Guidelines

- Be respectful and inclusive
- Help others learn
- Give constructive feedback
- Celebrate contributions

## Questions?

- **Email**: dmytro@termin-notify.de
- **GitHub Issues**: [Ask a question](https://github.com/dmankovsky/termin-notify/issues/new)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for making Termin-Notify better! 🎉
