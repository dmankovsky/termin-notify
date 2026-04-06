from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"  # 5 EUR/month - 3 services
    PRO = "pro"  # 10 EUR/month - unlimited services + SMS
    ENTERPRISE = "enterprise"  # Custom pricing


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    # Subscription
    subscription_tier = Column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    @property
    def max_services(self) -> int:
        """Maximum number of services user can monitor based on tier"""
        limits = {
            SubscriptionTier.FREE: 1,
            SubscriptionTier.BASIC: 3,
            SubscriptionTier.PRO: 999,
            SubscriptionTier.ENTERPRISE: 999,
        }
        return limits.get(self.subscription_tier, 1)

    @property
    def sms_enabled(self) -> bool:
        """Whether user can receive SMS notifications"""
        return self.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]
