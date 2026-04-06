from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import User, Notification
from app.models.notification import NotificationStatus
from app.api.auth import get_current_user

router = APIRouter()

# Schemas
class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    status: str
    subject: Optional[str]
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class UserDashboard(BaseModel):
    user: dict
    active_subscriptions: int
    total_notifications: int
    recent_notifications: List[NotificationResponse]

# Routes
@router.get("/dashboard", response_model=UserDashboard)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user dashboard data"""

    # Count active subscriptions
    from app.models import Subscription
    active_subs_result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.is_active == True
        )
    )
    active_subscriptions = len(active_subs_result.scalars().all())

    # Count total notifications
    total_notif_result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id)
    )
    total_notifications = len(total_notif_result.scalars().all())

    # Get recent notifications
    recent_result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(10)
    )
    recent_notifications = recent_result.scalars().all()

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "subscription_tier": current_user.subscription_tier.value,
            "max_services": current_user.max_services,
            "sms_enabled": current_user.sms_enabled,
        },
        "active_subscriptions": active_subscriptions,
        "total_notifications": total_notifications,
        "recent_notifications": recent_notifications,
    }

@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """Get user notifications"""

    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    notifications = result.scalars().all()

    return notifications
