from app.scrapers.base import BaseScraper
from app.scrapers.berlin import BerlinBuergeramtScraper
from app.scrapers.munich import MunichBuergeramtScraper
from app.scrapers.hamburg import HamburgBuergeramtScraper
from app.scrapers.frankfurt import FrankfurtBuergeramtScraper

__all__ = [
    "BaseScraper",
    "BerlinBuergeramtScraper",
    "MunichBuergeramtScraper",
    "HamburgBuergeramtScraper",
    "FrankfurtBuergeramtScraper",
]

# Scraper registry for dynamic loading
SCRAPER_REGISTRY = {
    "berlin_buergeramt": BerlinBuergeramtScraper,
    "munich_buergeramt": MunichBuergeramtScraper,
    "hamburg_buergeramt": HamburgBuergeramtScraper,
    "frankfurt_buergeramt": FrankfurtBuergeramtScraper,
}
