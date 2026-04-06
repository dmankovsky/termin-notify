from typing import List, Optional
from datetime import datetime
import re
import logging
from app.scrapers.base import BaseScraper, AppointmentSlot

logger = logging.getLogger(__name__)


class MunichBuergeramtScraper(BaseScraper):
    """
    Scraper for Munich Bürgeramt appointment system
    Munich uses terminvereinbarung-muenchen.de
    """

    BASE_URL = "https://terminvereinbarung-muenchen.de"

    async def scrape(self, url: str) -> List[AppointmentSlot]:
        """Scrape Munich Bürgeramt for available appointments"""
        appointments = []

        try:
            html = await self.fetch_page(url)
            if not html:
                return appointments

            soup = self.parse_html(html)

            # Check for "no appointments" message
            no_appointments = [
                "Keine freien Termine",
                "Aktuell keine Termine verfügbar",
            ]

            page_text = soup.get_text()
            if any(msg in page_text for msg in no_appointments):
                logger.info("No appointments available in Munich")
                return appointments

            # Munich often uses a table or list structure for appointments
            appointment_elements = soup.find_all(
                ["tr", "li", "div"],
                class_=re.compile(r"(termin|appointment|verfügbar|available)", re.I)
            )

            for elem in appointment_elements:
                try:
                    text = self.clean_text(elem.get_text())

                    # Look for date pattern
                    date_match = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", text)
                    if not date_match:
                        continue

                    day, month, year = date_match.groups()
                    appointment_date = datetime(int(year), int(month), int(day))

                    # Try to find booking link
                    link = elem.find("a")
                    booking_url = None
                    if link and link.get("href"):
                        href = link["href"]
                        booking_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                    slot = AppointmentSlot(
                        date=appointment_date,
                        appointment_type="Bürgeramt München",
                        location="München",
                        booking_url=booking_url,
                        raw_data={"text": text}
                    )
                    appointments.append(slot)

                except Exception as e:
                    logger.error(f"Error parsing Munich appointment: {e}")
                    continue

            logger.info(f"Found {len(appointments)} appointments in Munich")

        except Exception as e:
            logger.error(f"Error scraping Munich Bürgeramt: {e}")

        return appointments
