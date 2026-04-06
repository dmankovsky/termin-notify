from typing import List
from datetime import datetime
import re
import logging
from app.scrapers.base import BaseScraper, AppointmentSlot

logger = logging.getLogger(__name__)


class HamburgBuergeramtScraper(BaseScraper):
    """
    Scraper for Hamburg Bürgeramt appointment system
    Hamburg uses hamburg.de/terminvereinbarung
    """

    BASE_URL = "https://www.hamburg.de"

    async def scrape(self, url: str) -> List[AppointmentSlot]:
        """Scrape Hamburg Bürgeramt for available appointments"""
        appointments = []

        try:
            html = await self.fetch_page(url)
            if not html:
                return appointments

            soup = self.parse_html(html)

            # Check for availability indicator
            no_appointments = [
                "Keine Termine verfügbar",
                "Zurzeit keine freien Termine",
            ]

            page_text = soup.get_text()
            if any(msg in page_text for msg in no_appointments):
                logger.info("No appointments available in Hamburg")
                return appointments

            # Hamburg typically shows appointments in a calendar or list
            date_elements = soup.find_all(
                ["button", "a", "div"],
                class_=re.compile(r"(date|day|termin)", re.I)
            )

            for elem in date_elements:
                try:
                    # Check if element indicates availability
                    if "disabled" in elem.get("class", []) or elem.get("disabled"):
                        continue

                    text = self.clean_text(elem.get_text())
                    date_str = elem.get("data-date") or elem.get("value")

                    if date_str:
                        # Try ISO format first
                        try:
                            appointment_date = datetime.fromisoformat(date_str)
                        except:
                            # Try German format
                            match = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", str(date_str))
                            if match:
                                day, month, year = match.groups()
                                appointment_date = datetime(int(year), int(month), int(day))
                            else:
                                continue

                        link = elem if elem.name == "a" else elem.find("a")
                        booking_url = None
                        if link and link.get("href"):
                            href = link["href"]
                            booking_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                        slot = AppointmentSlot(
                            date=appointment_date,
                            appointment_type="Bürgeramt Hamburg",
                            location="Hamburg",
                            booking_url=booking_url,
                            raw_data={"text": text}
                        )
                        appointments.append(slot)

                except Exception as e:
                    logger.error(f"Error parsing Hamburg appointment: {e}")
                    continue

            logger.info(f"Found {len(appointments)} appointments in Hamburg")

        except Exception as e:
            logger.error(f"Error scraping Hamburg Bürgeramt: {e}")

        return appointments
