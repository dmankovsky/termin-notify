from typing import List
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
import json

from app.core.database import AsyncSessionLocal
from app.models import AppointmentService, AvailableAppointment, Subscription, User
from app.scrapers import SCRAPER_REGISTRY
from app.services.notification import NotificationService
from app.core.config import settings

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for monitoring appointment availability and sending notifications"""

    def __init__(self):
        self.notification_service = NotificationService()

    async def monitor_all_services(self):
        """Main monitoring task - scrapes all active services"""
        logger.info("Starting monitoring cycle...")

        async with AsyncSessionLocal() as db:
            # Get all active services
            result = await db.execute(
                select(AppointmentService).where(AppointmentService.is_active == True)
            )
            services = result.scalars().all()

            logger.info(f"Monitoring {len(services)} services")

            for service in services:
                try:
                    await self.monitor_service(service, db)
                except Exception as e:
                    logger.error(f"Error monitoring service {service.id}: {e}")
                    service.last_error = str(e)
                    service.last_scraped_at = datetime.utcnow()
                    await db.commit()

        logger.info("Monitoring cycle completed")

    async def monitor_service(self, service: AppointmentService, db):
        """Monitor a single appointment service"""

        logger.info(f"Monitoring: {service.name} ({service.city.value})")

        # Get scraper for this service
        scraper_class = SCRAPER_REGISTRY.get(service.scraper_type)
        if not scraper_class:
            logger.error(f"Unknown scraper type: {service.scraper_type}")
            return

        # Parse scraper config
        config = {}
        if service.scraper_config:
            try:
                config = json.loads(service.scraper_config)
            except:
                pass

        # Initialize scraper
        scraper = scraper_class(config=config)

        # Scrape for appointments
        try:
            appointments = await scraper.scrape(service.url)
            logger.info(f"Found {len(appointments)} appointments for {service.name}")

            # Update service status
            service.last_scraped_at = datetime.utcnow()
            service.last_success_at = datetime.utcnow()
            service.last_error = None

            # Process found appointments
            for appointment in appointments:
                await self.process_appointment(service, appointment, db)

            await db.commit()

        except Exception as e:
            logger.error(f"Error scraping {service.name}: {e}")
            service.last_scraped_at = datetime.utcnow()
            service.last_error = str(e)
            await db.commit()
            raise

    async def process_appointment(
        self,
        service: AppointmentService,
        appointment_slot,
        db,
    ):
        """Process a found appointment slot"""

        # Check if we already have this appointment
        query = select(AvailableAppointment).where(
            AvailableAppointment.service_id == service.id,
            AvailableAppointment.appointment_date == appointment_slot.date,
            AvailableAppointment.is_still_available == True,
        )

        result = await db.execute(query)
        existing = result.scalars().first()

        if existing:
            # Update existing appointment
            existing.checked_at = datetime.utcnow()
            logger.debug(f"Appointment already exists: {existing.id}")
            return

        # Create new appointment record
        new_appointment = AvailableAppointment(
            service_id=service.id,
            appointment_date=appointment_slot.date,
            appointment_type=appointment_slot.appointment_type,
            location=appointment_slot.location,
            booking_url=appointment_slot.booking_url,
            raw_data=json.dumps(appointment_slot.raw_data),
            is_still_available=True,
        )

        db.add(new_appointment)
        await db.flush()  # Get the ID

        logger.info(f"New appointment found: {new_appointment.id}")

        # Notify subscribed users
        await self.notify_subscribers(service, new_appointment, db)

    async def notify_subscribers(
        self,
        service: AppointmentService,
        appointment: AvailableAppointment,
        db,
    ):
        """Notify all users subscribed to this service"""

        # Get all active subscriptions for this service
        query = (
            select(Subscription)
            .options(selectinload(Subscription.user))
            .where(
                Subscription.service_id == service.id,
                Subscription.is_active == True,
            )
        )

        result = await db.execute(query)
        subscriptions = result.scalars().all()

        logger.info(f"Notifying {len(subscriptions)} subscribers")

        for subscription in subscriptions:
            try:
                # Check notification cooldown
                if subscription.last_notification_sent_at:
                    cooldown = timedelta(minutes=settings.NOTIFICATION_COOLDOWN_MINUTES)
                    if datetime.utcnow() - subscription.last_notification_sent_at < cooldown:
                        logger.debug(f"Skipping user {subscription.user_id} - cooldown active")
                        continue

                # Check daily notification limit
                if await self._user_exceeded_daily_limit(subscription.user, db):
                    logger.warning(f"User {subscription.user_id} exceeded daily notification limit")
                    continue

                # Check appointment filters
                if not self._matches_filters(appointment, subscription):
                    logger.debug(f"Appointment doesn't match user {subscription.user_id} filters")
                    continue

                # Send notification
                if subscription.notify_email:
                    success = await self.notification_service.send_appointment_notification(
                        user=subscription.user,
                        appointment=appointment,
                        db_session=db,
                    )

                    if success:
                        subscription.last_notification_sent_at = datetime.utcnow()
                        logger.info(f"Notified user {subscription.user.email}")

            except Exception as e:
                logger.error(f"Error notifying user {subscription.user_id}: {e}")

        await db.commit()

    def _matches_filters(
        self,
        appointment: AvailableAppointment,
        subscription: Subscription,
    ) -> bool:
        """Check if appointment matches user's filters"""

        # Check date range
        if subscription.date_range_start and appointment.appointment_date:
            if appointment.appointment_date < subscription.date_range_start:
                return False

        if subscription.date_range_end and appointment.appointment_date:
            if appointment.appointment_date > subscription.date_range_end:
                return False

        # Check appointment type filter
        if subscription.appointment_type_filter:
            try:
                allowed_types = json.loads(subscription.appointment_type_filter)
                if appointment.appointment_type not in allowed_types:
                    return False
            except:
                pass

        return True

    async def _user_exceeded_daily_limit(self, user: User, db) -> bool:
        """Check if user has exceeded daily notification limit"""

        from app.models.notification import Notification

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        query = select(Notification).where(
            Notification.user_id == user.id,
            Notification.created_at >= today_start,
        )

        result = await db.execute(query)
        count = len(result.scalars().all())

        return count >= settings.MAX_NOTIFICATIONS_PER_USER_PER_DAY
