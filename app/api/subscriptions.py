from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import Subscription, User, AppointmentService
from app.api.auth import get_current_user

router = APIRouter()

# Schemas
class SubscriptionCreate(BaseModel):
    service_id: int
    notify_email: bool = True
    notify_sms: bool = False
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None

class SubscriptionResponse(BaseModel):
    id: int
    service_id: int
    service_name: str
    service_city: str
    notify_email: bool
    notify_sms: bool
    is_active: bool
    created_at: datetime
    last_notification_sent_at: Optional[datetime]

    class Config:
        from_attributes = True

# Routes
@router.get("/", response_model=List[SubscriptionResponse])
async def list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all subscriptions for current user"""

    query = (
        select(Subscription)
        .options(selectinload(Subscription.service))
        .where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc())
    )

    result = await db.execute(query)
    subscriptions = result.scalars().all()

    # Format response
    response = []
    for sub in subscriptions:
        response.append({
            "id": sub.id,
            "service_id": sub.service_id,
            "service_name": sub.service.name,
            "service_city": sub.service.city.value,
            "notify_email": sub.notify_email,
            "notify_sms": sub.notify_sms,
            "is_active": sub.is_active,
            "created_at": sub.created_at,
            "last_notification_sent_at": sub.last_notification_sent_at,
        })

    return response

@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription"""

    # Check if service exists
    service_result = await db.execute(
        select(AppointmentService).where(AppointmentService.id == subscription_data.service_id)
    )
    service = service_result.scalars().first()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    # Check if subscription already exists
    existing_result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.service_id == subscription_data.service_id
        )
    )
    existing = existing_result.scalars().first()

    if existing:
        # Reactivate if inactive
        if not existing.is_active:
            existing.is_active = True
            await db.commit()
            await db.refresh(existing)
            return {
                "id": existing.id,
                "service_id": existing.service_id,
                "service_name": service.name,
                "service_city": service.city.value,
                "notify_email": existing.notify_email,
                "notify_sms": existing.notify_sms,
                "is_active": existing.is_active,
                "created_at": existing.created_at,
                "last_notification_sent_at": existing.last_notification_sent_at,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription already exists"
            )

    # Check subscription limits
    active_subs_result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.is_active == True
        )
    )
    active_subs_count = len(active_subs_result.scalars().all())

    if active_subs_count >= current_user.max_services:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Maximum number of subscriptions reached ({current_user.max_services}). Upgrade your plan."
        )

    # Check SMS permission
    if subscription_data.notify_sms and not current_user.sms_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SMS notifications require PRO plan"
        )

    # Create subscription
    subscription = Subscription(
        user_id=current_user.id,
        service_id=subscription_data.service_id,
        notify_email=subscription_data.notify_email,
        notify_sms=subscription_data.notify_sms,
        date_range_start=subscription_data.date_range_start,
        date_range_end=subscription_data.date_range_end,
        is_active=True,
    )

    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)

    return {
        "id": subscription.id,
        "service_id": subscription.service_id,
        "service_name": service.name,
        "service_city": service.city.value,
        "notify_email": subscription.notify_email,
        "notify_sms": subscription.notify_sms,
        "is_active": subscription.is_active,
        "created_at": subscription.created_at,
        "last_notification_sent_at": subscription.last_notification_sent_at,
    }

@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete/deactivate a subscription"""

    result = await db.execute(
        select(Subscription).where(
            Subscription.id == subscription_id,
            Subscription.user_id == current_user.id
        )
    )
    subscription = result.scalars().first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    # Soft delete - just deactivate
    subscription.is_active = False
    await db.commit()

    return {"message": "Subscription deactivated successfully"}
