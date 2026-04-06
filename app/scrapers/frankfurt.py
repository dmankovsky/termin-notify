from typing import List
from datetime import datetime
import re
import logging
from app.scrapers.base import BaseScraper, AppointmentSlot

logger = logging.getLogger(__name__)


class FrankfurtBuergeramtScraper(BaseScraper):
    """
    Scraper for Frankfurt Bürgeramt appointment system
    Frankfurt uses frankfurt.de/terminvereinbarung
    """

    BASE_URL = "https://www.frankfurt.de"

    async def scrape(self, url: str) -> List[AppointmentSlot]:
        """Scrape Frankfurt Bürgeramt for available appointments"""
        appointments = []

        try:
            html = await self.fetch_page(url)
            if not html:
                return appointments

            soup = self.parse_html(html)

            # Check for no appointments message
            no_appointments = [
                "Keine freien Termine",
                "Keine Termine verfügbar",
            ]

            page_text = soup.get_text()
            if any(msg in page_text for msg in no_appointments):
                logger.info("No appointments available in Frankfurt")
                return appointments

            # Look for appointment slots
            slots = soup.find_all(
                ["div", "li", "tr"],
                class_=re.compile(r"(slot|termin|appointment)", re.I)
            )

            for slot_elem in slots:
                try:
                    text = self.clean_text(slot_elem.get_text())

                    # Extract date
                    date_match = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", text)
                    if not date_match:
                        continue

                    day, month, year = date_match.groups()
                    appointment_date = datetime(int(year), int(month), int(day))

                    # Try to find booking link
                    link = slot_elem.find("a")
                    booking_url = None
                    if link and link.get("href"):
                        href = link["href"]
                        booking_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                    # Try to extract specific location/office
                    location = "Frankfurt"
                    location_elem = slot_elem.find(class_=re.compile(r"(location|standort)", re.I))
                    if location_elem:
                        location = self.clean_text(location_elem.get_text())

                    slot = AppointmentSlot(
                        date=appointment_date,
                        appointment_type="Bürgeramt Frankfurt",
                        location=location,
                        booking_url=booking_url,
                        raw_data={"text": text}
                    )
                    appointments.append(slot)

                except Exception as e:
                    logger.error(f"Error parsing Frankfurt appointment: {e}")
                    continue

            logger.info(f"Found {len(appointments)} appointments in Frankfurt")

        except Exception as e:
            logger.error(f"Error scraping Frankfurt Bürgeramt: {e}")

        return appointments
