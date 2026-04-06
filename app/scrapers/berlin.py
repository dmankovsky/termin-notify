from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import json
import logging
from app.scrapers.base import BaseScraper, AppointmentSlot

logger = logging.getLogger(__name__)


class BerlinBuergeramtScraper(BaseScraper):
    """
    Scraper for Berlin Bürgeramt appointment system
    Berlin uses a centralized booking system at service.berlin.de
    """

    BASE_URL = "https://service.berlin.de"

    async def scrape(self, url: str) -> List[AppointmentSlot]:
        """
        Scrape Berlin Bürgeramt for available appointments

        Berlin's system typically works like this:
        1. Service selection page
        2. Location selection
        3. Calendar with available dates
        """
        appointments = []

        try:
            html = await self.fetch_page(url)
            if not html:
                return appointments

            soup = self.parse_html(html)

            # Check for "no appointments available" message
            no_appointment_indicators = [
                "Keine Termine verfügbar",
                "Es sind aktuell keine Termine verfügbar",
                "Derzeit stehen leider keine Termine zur Verfügung",
            ]

            page_text = soup.get_text()
            if any(indicator in page_text for indicator in no_appointment_indicators):
                logger.info("No appointments available (message found)")
                return appointments

            # Look for calendar elements or appointment links
            # Berlin typically shows available dates as clickable elements
            calendar_days = soup.find_all(class_=re.compile(r"calendar.*day.*available", re.I))
            appointment_links = soup.find_all("a", href=re.compile(r"(termin|appointment)"))

            for day in calendar_days:
                try:
                    # Try to extract date from various attributes
                    date_str = (
                        day.get("data-date") or
                        day.get("data-value") or
                        day.get_text(strip=True)
                    )

                    appointment_date = self._parse_date(date_str)
                    if not appointment_date:
                        continue

                    # Look for booking link
                    booking_link = day.find("a")
                    booking_url = None
                    if booking_link and booking_link.get("href"):
                        href = booking_link["href"]
                        booking_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                    # Extract location/office info
                    location = self._extract_location(day)

                    slot = AppointmentSlot(
                        date=appointment_date,
                        appointment_type="Bürgeramt",
                        location=location,
                        booking_url=booking_url,
                        raw_data={
                            "source": "berlin_service",
                            "html_class": day.get("class"),
                        }
                    )
                    appointments.append(slot)

                except Exception as e:
                    logger.error(f"Error parsing appointment slot: {e}")
                    continue

            # Also check for direct appointment links in lists
            for link in appointment_links:
                try:
                    link_text = self.clean_text(link.get_text())
                    if not link_text or len(link_text) < 5:
                        continue

                    # Try to extract date from link text
                    date_match = re.search(
                        r"(\d{1,2})\.(\d{1,2})\.(\d{4})",
                        link_text
                    )

                    if date_match:
                        day, month, year = date_match.groups()
                        appointment_date = datetime(int(year), int(month), int(day))

                        href = link["href"]
                        booking_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                        slot = AppointmentSlot(
                            date=appointment_date,
                            appointment_type="Bürgeramt",
                            location="Berlin",
                            booking_url=booking_url,
                            raw_data={"link_text": link_text}
                        )
                        appointments.append(slot)

                except Exception as e:
                    logger.error(f"Error parsing link: {e}")
                    continue

            logger.info(f"Found {len(appointments)} appointments in Berlin")

        except Exception as e:
            logger.error(f"Error scraping Berlin Bürgeramt: {e}")

        return appointments

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime object"""
        if not date_str:
            return None

        # Try different date formats
        formats = [
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None

    def _extract_location(self, element) -> str:
        """Extract location/office name from element"""
        # Look for common location indicators
        location_classes = ["location", "office", "standort", "amt"]

        for cls in location_classes:
            loc_elem = element.find(class_=re.compile(cls, re.I))
            if loc_elem:
                return self.clean_text(loc_elem.get_text())

        # Default to Berlin if specific location not found
        return "Berlin"
