from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ServiceType(str, enum.Enum):
    BUERGERAMT = "buergeramt"
    AUSLAENDERBEHORDE = "auslaenderbehorde"
    KFZ_ZULASSUNG = "kfz_zulassung"
    FUEHRERSCHEIN = "fuehrerschein"
    OTHER = "other"


class City(str, enum.Enum):
    BERLIN = "berlin"
    MUNICH = "munich"
    HAMBURG = "hamburg"
    FRANKFURT = "frankfurt"
    COLOGNE = "cologne"
    STUTTGART = "stuttgart"
    DUSSELDORF = "dusseldorf"


class AppointmentService(Base):
    """Represents a monitored appointment service (e.g., Berlin Bürgeramt Mitte)"""
    __tablename__ = "appointment_services"

    id = Column(Integer, primary_key=True, index=True)

    # Identification
    name = Column(String, nullable=False)  # e.g., "Bürgeramt Mitte"
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    city = Column(SQLEnum(City), nullable=False)

    # Scraping details
    url = Column(String, nullable=False)
    scraper_type = Column(String, nullable=False)  # Which scraper class to use
    scraper_config = Column(Text, nullable=True)  # JSON config for scraper

    # Status
    is_active = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    available_appointments = relationship(
        "AvailableAppointment",
        back_populates="service",
        cascade="all, delete-orphan"
    )
    subscriptions = relationship(
        "Subscription",
        back_populates="service",
        cascade="all, delete-orphan"
    )


class AvailableAppointment(Base):
    """Represents a found available appointment slot"""
    __tablename__ = "available_appointments"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("appointment_services.id"), nullable=False)

    # Appointment details
    appointment_date = Column(DateTime(timezone=True), nullable=True)
    appointment_type = Column(String, nullable=True)  # e.g., "Anmeldung", "Personalausweis"
    location = Column(String, nullable=True)
    booking_url = Column(String, nullable=True)

    # Metadata
    raw_data = Column(Text, nullable=True)  # JSON with full scraped data
    is_still_available = Column(Boolean, default=True)

    # Timestamps
    found_at = Column(DateTime(timezone=True), server_default=func.now())
    checked_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    service = relationship("AppointmentService", back_populates="available_appointments")
