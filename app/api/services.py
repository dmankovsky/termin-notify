from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import AppointmentService
from app.models.appointment import City, ServiceType

router = APIRouter()

# Schemas
class AppointmentServiceResponse(BaseModel):
    id: int
    name: str
    service_type: str
    city: str
    url: str
    is_active: bool
    last_scraped_at: Optional[datetime]
    last_success_at: Optional[datetime]

    class Config:
        from_attributes = True

# Routes
@router.get("/", response_model=List[AppointmentServiceResponse])
async def list_services(
    city: Optional[str] = Query(None),
    service_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List all available appointment services"""

    query = select(AppointmentService).where(AppointmentService.is_active == True)

    if city:
        try:
            city_enum = City(city.lower())
            query = query.where(AppointmentService.city == city_enum)
        except ValueError:
            pass

    if service_type:
        try:
            type_enum = ServiceType(service_type.lower())
            query = query.where(AppointmentService.service_type == type_enum)
        except ValueError:
            pass

    result = await db.execute(query)
    services = result.scalars().all()

    return services

@router.get("/{service_id}", response_model=AppointmentServiceResponse)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific appointment service"""

    result = await db.execute(
        select(AppointmentService).where(AppointmentService.id == service_id)
    )
    service = result.scalars().first()

    if not service:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Service not found")

    return service

@router.get("/cities/list")
async def list_cities():
    """List all available cities"""
    return [{"value": city.value, "name": city.name} for city in City]

@router.get("/types/list")
async def list_service_types():
    """List all available service types"""
    return [{"value": st.value, "name": st.name} for st in ServiceType]
