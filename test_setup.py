"""
Test script to validate the Termin-Notify setup
Creates a test user and subscription
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models import User, AppointmentService, Subscription
from app.models.user import SubscriptionTier
from app.api.auth import get_password_hash
from sqlalchemy import select


async def create_test_user():
    """Create a test user and subscription"""

    async with AsyncSessionLocal() as db:
        # Create test user
        test_email = "test@example.com"

        # Check if user exists
        result = await db.execute(select(User).where(User.email == test_email))
        user = result.scalars().first()

        if not user:
            user = User(
                email=test_email,
                hashed_password=get_password_hash("testpassword123"),
                full_name="Test User",
                subscription_tier=SubscriptionTier.FREE,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"✅ Created test user: {user.email}")
        else:
            print(f"ℹ️  Test user already exists: {user.email}")

        # Get first service
        result = await db.execute(select(AppointmentService).limit(1))
        service = result.scalars().first()

        if not service:
            print("❌ No services found in database. Run init_db.py first!")
            return

        # Check if subscription exists
        result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.service_id == service.id
            )
        )
        subscription = result.scalars().first()

        if not subscription:
            subscription = Subscription(
                user_id=user.id,
                service_id=service.id,
                notify_email=True,
                is_active=True,
            )
            db.add(subscription)
            await db.commit()
            print(f"✅ Created subscription to: {service.name}")
        else:
            print(f"ℹ️  Subscription already exists to: {service.name}")

        print("\n" + "="*50)
        print("TEST USER CREDENTIALS")
        print("="*50)
        print(f"Email: {test_email}")
        print(f"Password: testpassword123")
        print(f"Subscription Tier: {user.subscription_tier.value}")
        print("="*50)
        print("\nYou can now login using these credentials!")


async def run_test_scraper():
    """Test scraping a service"""
    from app.scrapers.berlin import BerlinBuergeramtScraper

    print("\n" + "="*50)
    print("TESTING SCRAPER")
    print("="*50)

    scraper = BerlinBuergeramtScraper()

    # Test with Berlin Bürgeramt URL
    test_url = "https://service.berlin.de/terminvereinbarung/termin/all/120686/"

    print(f"Scraping: {test_url}")
    print("Please wait...")

    try:
        appointments = await scraper.scrape(test_url)
        print(f"\n✅ Scraper completed successfully!")
        print(f"Found {len(appointments)} appointments")

        if appointments:
            print("\nFirst appointment:")
            apt = appointments[0]
            print(f"  Date: {apt.date}")
            print(f"  Type: {apt.appointment_type}")
            print(f"  Location: {apt.location}")
            print(f"  URL: {apt.booking_url}")
    except Exception as e:
        print(f"\n❌ Scraper failed: {e}")


async def main():
    """Run all tests"""
    print("="*50)
    print("TERMIN-NOTIFY SETUP TEST")
    print("="*50)

    # Create test user
    await create_test_user()

    # Test scraper
    await run_test_scraper()

    print("\n" + "="*50)
    print("NEXT STEPS")
    print("="*50)
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Visit API docs: http://localhost:8000/docs")
    print("3. Test login with credentials above")
    print("4. Create subscriptions via API")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
