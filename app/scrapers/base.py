from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class AppointmentSlot:
    """Represents a single available appointment slot"""

    def __init__(
        self,
        date: Optional[datetime] = None,
        appointment_type: Optional[str] = None,
        location: Optional[str] = None,
        booking_url: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None,
    ):
        self.date = date
        self.appointment_type = appointment_type
        self.location = location
        self.booking_url = booking_url
        self.raw_data = raw_data or {}


class BaseScraper(ABC):
    """Base class for all appointment scrapers"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.user_agent = self.config.get(
            "user_agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

    async def fetch_page(self, url: str, timeout: int = 30) -> Optional[str]:
        """Fetch HTML content from URL"""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup"""
        return BeautifulSoup(html, "lxml")

    @abstractmethod
    async def scrape(self, url: str) -> List[AppointmentSlot]:
        """
        Main scraping method - must be implemented by each scraper
        Returns list of available appointment slots
        """
        pass

    async def check_availability(self, url: str) -> bool:
        """Quick check if appointments are available"""
        slots = await self.scrape(url)
        return len(slots) > 0

    def clean_text(self, text: Optional[str]) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return " ".join(text.strip().split())
