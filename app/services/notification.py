import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
import logging
from jinja2 import Template

from app.core.config import settings
from app.models import User, AvailableAppointment, Notification
from app.models.notification import NotificationType, NotificationStatus

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications to users"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email using SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email

            # Add text version
            if text_content:
                message.attach(MIMEText(text_content, "plain"))

            # Add HTML version
            message.attach(MIMEText(html_content, "html"))

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True,
            )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_appointment_notification(
        self,
        user: User,
        appointment: AvailableAppointment,
        db_session,
    ) -> bool:
        """Send notification about available appointment"""

        # Create email content
        subject = f"🎉 Termin verfügbar: {appointment.service.name}"

        html_content = self._create_appointment_email_html(user, appointment)
        text_content = self._create_appointment_email_text(user, appointment)

        # Send email
        success = await self.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

        # Log notification in database
        notification = Notification(
            user_id=user.id,
            appointment_id=appointment.id,
            notification_type=NotificationType.EMAIL,
            status=NotificationStatus.SENT if success else NotificationStatus.FAILED,
            recipient=user.email,
            subject=subject,
            message=html_content,
            sent_at=datetime.utcnow() if success else None,
        )
        db_session.add(notification)
        await db_session.commit()

        return success

    def _create_appointment_email_html(
        self,
        user: User,
        appointment: AvailableAppointment,
    ) -> str:
        """Create HTML email content for appointment notification"""

        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
        .content { background-color: #f9f9f9; padding: 20px; margin: 20px 0; }
        .appointment-details { background-color: white; padding: 15px; border-left: 4px solid #4CAF50; }
        .button { display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 15px 0; }
        .footer { text-align: center; color: #666; font-size: 12px; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Termin verfügbar!</h1>
        </div>

        <div class="content">
            <p>Hallo {{ user_name }},</p>

            <p>Gute Nachrichten! Wir haben einen verfügbaren Termin für Sie gefunden:</p>

            <div class="appointment-details">
                <h3>{{ service_name }}</h3>
                <p><strong>Ort:</strong> {{ location }}</p>
                {% if appointment_date %}
                <p><strong>Datum:</strong> {{ appointment_date }}</p>
                {% endif %}
                {% if appointment_type %}
                <p><strong>Art:</strong> {{ appointment_type }}</p>
                {% endif %}
            </div>

            {% if booking_url %}
            <p style="text-align: center;">
                <a href="{{ booking_url }}" class="button">Jetzt Termin buchen</a>
            </p>
            <p style="font-size: 12px; color: #666;">
                Link: <a href="{{ booking_url }}">{{ booking_url }}</a>
            </p>
            {% else %}
            <p><strong>Hinweis:</strong> Bitte prüfen Sie die Website direkt für die Buchung.</p>
            {% endif %}

            <p style="color: #e74c3c; font-weight: bold;">⚠️ Termine sind oft schnell ausgebucht. Bitte buchen Sie zeitnah!</p>
        </div>

        <div class="footer">
            <p>Termin-Notify - Ihr Termin-Benachrichtigungsservice</p>
            <p>Sie erhalten diese E-Mail, weil Sie sich für Benachrichtigungen angemeldet haben.</p>
        </div>
    </div>
</body>
</html>
        """)

        return template.render(
            user_name=user.full_name or user.email.split("@")[0],
            service_name=appointment.service.name,
            location=appointment.location or appointment.service.city.value,
            appointment_date=appointment.appointment_date.strftime("%d.%m.%Y %H:%M") if appointment.appointment_date else None,
            appointment_type=appointment.appointment_type,
            booking_url=appointment.booking_url,
        )

    def _create_appointment_email_text(
        self,
        user: User,
        appointment: AvailableAppointment,
    ) -> str:
        """Create plain text email content for appointment notification"""

        text = f"""
Hallo {user.full_name or user.email.split("@")[0]},

Gute Nachrichten! Wir haben einen verfügbaren Termin für Sie gefunden:

{appointment.service.name}
Ort: {appointment.location or appointment.service.city.value}
"""

        if appointment.appointment_date:
            text += f"Datum: {appointment.appointment_date.strftime('%d.%m.%Y %H:%M')}\n"

        if appointment.appointment_type:
            text += f"Art: {appointment.appointment_type}\n"

        if appointment.booking_url:
            text += f"\nJetzt buchen: {appointment.booking_url}\n"

        text += """
WICHTIG: Termine sind oft schnell ausgebucht. Bitte buchen Sie zeitnah!

---
Termin-Notify - Ihr Termin-Benachrichtigungsservice
"""

        return text

    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new user"""

        subject = "Willkommen bei Termin-Notify!"

        html_content = f"""
        <h2>Willkommen bei Termin-Notify!</h2>
        <p>Hallo {user.full_name or user.email.split("@")[0]},</p>
        <p>Vielen Dank für Ihre Registrierung bei Termin-Notify.</p>
        <p>Wir benachrichtigen Sie sofort, wenn Termine für Ihre ausgewählten Services verfügbar werden.</p>
        <p>Viel Erfolg bei der Terminsuche!</p>
        """

        return await self.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
        )
