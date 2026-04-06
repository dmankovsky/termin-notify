"""
Database initialization script
Creates tables and adds initial appointment services
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine, Base, AsyncSessionLocal
from app.models import AppointmentService
from app.models.appointment import City, ServiceType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


INITIAL_SERVICES = [
    # Berlin
    {
        "name": "Bürgeramt Berlin Mitte",
        "service_type": ServiceType.BUERGERAMT,
        "city": City.BERLIN,
        "url": "https://service.berlin.de/terminvereinbarung/termin/all/120686/",
        "scraper_type": "berlin_buergeramt",
    },
    {
        "name": "Bürgeramt Berlin Charlottenburg-Wilmersdorf",
        "service_type": ServiceType.BUERGERAMT,
        "city": City.BERLIN,
        "url": "https://service.berlin.de/terminvereinbarung/termin/all/120335/",
        "scraper_type": "berlin_buergeramt",
    },
    {
        "name": "Landesamt für Einwanderung Berlin",
        "service_type": ServiceType.AUSLAENDERBEHORDE,
        "city": City.BERLIN,
        "url": "https://service.berlin.de/terminvereinbarung/termin/all/324269/",
        "scraper_type": "berlin_buergeramt",
    },

    # Munich
    {
        "name": "Bürgeramt München Hauptstandort",
        "service_type": ServiceType.BUERGERAMT,
        "city": City.MUNICH,
        "url": "https://stadt.muenchen.de/terminvereinbarung.html",
        "scraper_type": "munich_buergeramt",
    },

    # Hamburg
    {
        "name": "Kundenzentrum Hamburg Mitte",
        "service_type": ServiceType.BUERGERAMT,
        "city": City.HAMBURG,
        "url": "https://serviceportal.hamburg.de/termin/",
        "scraper_type": "hamburg_buergeramt",
    },

    # Frankfurt
    {
        "name": "Bürgeramt Frankfurt Mitte",
        "service_type": ServiceType.BUERGERAMT,
        "city": City.FRANKFURT,
        "url": "https://www.frankfurt.de/service-und-rathaus/verwaltung/aemter-und-institutionen/buergeramt",
        "scraper_type": "frankfurt_buergeramt",
    },
]


async def init_database():
    """Initialize database with tables and seed data"""

    logger.info("Initializing database...")

    # Create all tables
    async with engine.begin() as conn:
        logger.info("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully")

    # Add initial services
    async with AsyncSessionLocal() as session:
        logger.info("Adding initial appointment services...")

        for service_data in INITIAL_SERVICES:
            # Check if service already exists
            result = await session.execute(
                text("SELECT id FROM appointment_services WHERE name = :name"),
                {"name": service_data["name"]}
            )
            existing = result.first()

            if not existing:
                service = AppointmentService(**service_data)
                session.add(service)
                logger.info(f"Added service: {service_data['name']}")
            else:
                logger.info(f"Service already exists: {service_data['name']}")

        await session.commit()
        logger.info("Database initialization completed!")


async def drop_all_tables():
    """Drop all tables (use with caution!)"""
    logger.warning("DROPPING ALL TABLES...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("All tables dropped")


if __name__ == "__main__":
    # Run initialization
    asyncio.run(init_database())
