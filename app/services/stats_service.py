from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from app.models.property import Property, PropertyStatus
from app.models.customer import Customer
from app.models.user import User, UserRole

class StatsService:
    
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> Dict[str, Any]:
        """Admin və Managerlər üçün qlobal dashboard statistikası qaytarır"""
        
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        
        # 1. Aktiv Agent Sayı
        stmt_active_agents = select(func.count(User.id)).where(
            User.is_active == True, 
            User.role == UserRole.AGENT
        )
        active_agents = (await db.execute(stmt_active_agents)).scalar() or 0

        # 2. Ümumi Aktiv Evlər
        stmt_active_properties = select(func.count(Property.id)).where(Property.status == PropertyStatus.ACTIVE)
        active_properties = (await db.execute(stmt_active_properties)).scalar() or 0
        
        # 3. Bu gün əlavə edilən yeni evlər
        stmt_today_properties = select(func.count(Property.id)).where(Property.created_at >= today_start)
        today_properties = (await db.execute(stmt_today_properties)).scalar() or 0

        # 4. Bu gün əlavə edilən müştərilər
        stmt_today_customers = select(func.count(Customer.id)).where(Customer.created_at >= today_start)
        today_customers = (await db.execute(stmt_today_customers)).scalar() or 0
        
        # 5. Satılmış evlərin ümumi dövriyyəsi (Gəlir ehtimalı - sadə hesablama üçün qiymətlərin cəmi)
        stmt_sold_revenue = select(func.sum(Property.price)).where(Property.status == PropertyStatus.SOLD)
        total_sold_revenue = (await db.execute(stmt_sold_revenue)).scalar() or 0.0

        return {
            "active_agents": active_agents,
            "active_properties": active_properties,
            "today_new_properties": today_properties,
            "today_new_customers": today_customers,
            "total_sold_revenue": total_sold_revenue
        }
