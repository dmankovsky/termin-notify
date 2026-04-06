#!/usr/bin/env python3
"""
Management CLI for Termin-Notify
"""
import asyncio
import sys
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import User, AppointmentService, Subscription, AvailableAppointment
from app.core.init_db import init_database, drop_all_tables


async def list_users():
    """List all users"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

        print(f"\n{'='*80}")
        print(f"{'ID':<5} {'Email':<30} {'Tier':<15} {'Active':<10}")
        print(f"{'='*80}")

        for user in users:
            print(
                f"{user.id:<5} {user.email:<30} "
                f"{user.subscription_tier.value:<15} {'Yes' if user.is_active else 'No':<10}"
            )

        print(f"{'='*80}")
        print(f"Total: {len(users)} users\n")


async def list_services():
    """List all appointment services"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AppointmentService))
        services = result.scalars().all()

        print(f"\n{'='*100}")
        print(f"{'ID':<5} {'Name':<40} {'City':<15} {'Type':<20} {'Active':<10}")
        print(f"{'='*100}")

        for service in services:
            print(
                f"{service.id:<5} {service.name:<40} "
                f"{service.city.value:<15} {service.service_type.value:<20} "
                f"{'Yes' if service.is_active else 'No':<10}"
            )

        print(f"{'='*100}")
        print(f"Total: {len(services)} services\n")


async def list_subscriptions():
    """List all subscriptions"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Subscription).join(User).join(AppointmentService)
        )
        subscriptions = result.scalars().all()

        print(f"\n{'='*100}")
        print(f"{'ID':<5} {'User':<30} {'Service':<35} {'Email':<8} {'Active':<10}")
        print(f"{'='*100}")

        for sub in subscriptions:
            print(
                f"{sub.id:<5} {sub.user.email:<30} "
                f"{sub.service.name[:33]:<35} "
                f"{'Yes' if sub.notify_email else 'No':<8} "
                f"{'Yes' if sub.is_active else 'No':<10}"
            )

        print(f"{'='*100}")
        print(f"Total: {len(subscriptions)} subscriptions\n")


async def stats():
    """Show database statistics"""
    async with AsyncSessionLocal() as db:
        user_count = len((await db.execute(select(User))).scalars().all())
        service_count = len((await db.execute(select(AppointmentService))).scalars().all())
        subscription_count = len((await db.execute(select(Subscription))).scalars().all())
        appointment_count = len((await db.execute(select(AvailableAppointment))).scalars().all())

        active_subs = len(
            (await db.execute(
                select(Subscription).where(Subscription.is_active == True)
            )).scalars().all()
        )

        print(f"\n{'='*50}")
        print(f"TERMIN-NOTIFY STATISTICS")
        print(f"{'='*50}")
        print(f"Total Users: {user_count}")
        print(f"Total Services: {service_count}")
        print(f"Total Subscriptions: {subscription_count}")
        print(f"  - Active: {active_subs}")
        print(f"  - Inactive: {subscription_count - active_subs}")
        print(f"Appointments Found: {appointment_count}")
        print(f"{'='*50}\n")


def print_help():
    """Print help message"""
    print("""
Termin-Notify Management CLI

Usage:
    python manage.py <command>

Commands:
    init            Initialize database and create tables
    reset           Drop all tables and reinitialize (CAUTION!)
    users           List all users
    services        List all appointment services
    subscriptions   List all subscriptions
    stats           Show database statistics
    help            Show this help message

Examples:
    python manage.py init
    python manage.py users
    python manage.py stats
    """)


async def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "help":
        print_help()

    elif command == "init":
        print("Initializing database...")
        await init_database()

    elif command == "reset":
        confirm = input("⚠️  This will DELETE all data! Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            await drop_all_tables()
            await init_database()
            print("✅ Database reset complete")
        else:
            print("Cancelled")

    elif command == "users":
        await list_users()

    elif command == "services":
        await list_services()

    elif command == "subscriptions":
        await list_subscriptions()

    elif command == "stats":
        await stats()

    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    asyncio.run(main())
